/* 
	# 
	# Bases de Dados 2020/2021
	# Trabalho Prático
	#
*/

/* Cria a tabela dos utilizadores */
CREATE TABLE auction_user (
	user_id     SERIAL  UNIQUE  NOT NULL,
	username    VARCHAR(20)     NOT NULL,
	password    VARCHAR(20)     NOT NULL,
	email       VARCHAR(50)     NOT NULL,
	auth_token  INT		UNIQUE,

	PRIMARY KEY (username)
);


/* Cria a tabela dos leiloes */
CREATE TABLE auction (
	auction_id  VARCHAR(13)  UNIQUE  NOT NULL,
	title       VARCHAR(20)     NOT NULL,
	description VARCHAR(100)    NOT NULL,
	date_start  TIMESTAMP		NOT NULL,
	date_end    TIMESTAMP       NOT NULL,
	price_min   FLOAT(2)        NOT NULL,
	price_final FLOAT(2),
    is_finished INT             NOT NULL,
    winner_id   INT,
	user_id     INT             NOT NULL,
    version     INT             NOT NULL,

	PRIMARY KEY (auction_id)
);


/* Cria tabela para guardar as versoes passadas dos leiloes */
CREATE TABLE auction_backup (
	auction_id  VARCHAR(13)		NOT NULL,
	title       VARCHAR(20)     NOT NULL,
	description VARCHAR(100)    NOT NULL,
	date_start  TIMESTAMP		NOT NULL,
	date_end    TIMESTAMP       NOT NULL,
	price_min   FLOAT(2)        NOT NULL,
	user_id     INT             NOT NULL,
	version		INT             NOT NULL
);


/* Cria a tabela com as licitacoes */
CREATE TABLE bid (
	bid_id		SERIAL UNIQUE	NOT NULL,
	date        TIMESTAMP     	NOT NULL,
	value       FLOAT(2)      	NOT NULL,
	user_id     INT	        	NOT NULL,
	auction_id  VARCHAR(13)	    NOT NULL,

	PRIMARY KEY (bid_id)
);


/* Cria a tabela das mensagens */
CREATE TABLE auction_msg (
	msg_id		SERIAL	UNIQUE,
	date        TIMESTAMP     	NOT NULL,
	message     VARCHAR(500)  	NOT NULL,
	user_id     INT	        	NOT NULL,
	auction_id  VARCHAR(13)    	NOT NULL,

	PRIMARY KEY (msg_id)
);


/* Cria a tabela das notificacoes de mensagens no mural */
CREATE TABLE message_notification (
	date        TIMESTAMP       NOT NULL,
	message     VARCHAR(500)    NOT NULL,
	auction_id  VARCHAR(13)	    NOT NULL,
	user_id     INT          	NOT NULL
);


/* Cria a tabela das notificaoes de licitacoes */
CREATE TABLE bid_notification (
	date        TIMESTAMP       NOT NULL,
	message     VARCHAR(500)    NOT NULL,
	auction_id  VARCHAR(13)    	NOT NULL,
	user_id		INT				NOT NULL
);


ALTER TABLE auction ADD CONSTRAINT auction_fk1 FOREIGN KEY (user_id) REFERENCES auction_user(user_id);
ALTER TABLE auction ADD CONSTRAINT auction_fk2 FOREIGN KEY (winner_id) REFERENCES auction_user(user_id);
ALTER TABLE auction_msg ADD CONSTRAINT msg_fk1 FOREIGN KEY (user_id) REFERENCES auction_user(user_id);
ALTER TABLE auction_msg ADD CONSTRAINT msg_fk2 FOREIGN KEY (auction_id) REFERENCES auction(auction_id);
ALTER TABLE bid ADD CONSTRAINT bid_fk1 FOREIGN KEY (user_id) REFERENCES auction_user(user_id);
ALTER TABLE bid ADD CONSTRAINT bid_fk2 FOREIGN KEY (auction_id) REFERENCES auction(auction_id);
ALTER TABLE message_notification ADD CONSTRAINT notif_fk1 FOREIGN KEY (user_id) REFERENCES auction_user(user_id);
ALTER TABLE message_notification ADD CONSTRAINT notif_fk2 FOREIGN KEY (auction_id) REFERENCES auction(auction_id);
ALTER TABLE bid_notification ADD CONSTRAINT bid_notif_fk1 FOREIGN KEY (auction_id) REFERENCES auction(auction_id);
ALTER TABLE bid_notification ADD CONSTRAINT bid_notif_fk2 FOREIGN KEY (user_id) REFERENCES auction_user(user_id);


/* funcao para inserir na tabela de notificacoes quando houver uma licitacao superior  */
create or replace function notify_bid_func() returns trigger
language plpgsql
as $$
declare
	c1 cursor for
		SELECT DISTINCT user_id, auction_id
		FROM bid
		WHERE auction_id = new.auction_id AND new.value > value;
begin
    raise notice 'Value: %', new."auction_id";
	for i in c1
	loop
        SET TIMEZONE='Europe/Lisbon';
		insert into bid_notification(date, message, auction_id, user_id)
		values(current_timestamp, CONCAT('Houve uma licitacao superior neste leilao: ', new.value), i.auction_id, i.user_id);
	end loop;
	return new;
end;
$$;


/* Trigger que chama a funcao para inserir notificacoes quando ocorrer uma licitacao */
create trigger notify_bid
after INSERT on bid
for each row 
execute procedure notify_bid_func();
	

/* funcao que insere na tabela de notificacoes de mensagens */ 
/* quero inserir sempre que: - alguem escreve num leilao criado por mim
                            - alguem escreve num leilao que eu escrevi*/
                                                                       
create or replace function notify_owner_func() returns trigger
language plpgsql
as $$
declare
    c2 cursor for
        SELECT DISTINCT user_id            
        FROM auction
        WHERE auction_id = new.auction_id
        UNION
        SELECT DISTINCT user_id            
        FROM auction_msg
        WHERE auction_id = new.auction_id AND user_id != new.user_id;
begin
    for i in c2
    loop
        SET TIMEZONE='Europe/Lisbon';
        insert into message_notification(date, message, auction_id, user_id)
        values(current_timestamp, CONCAT('Nova mensagem no mural deste leilao: ', new.message), new.auction_id, i.user_id);
    end loop;
    return new;
end;
$$;


create trigger notify_owner
after INSERT on auction_msg
for each row
execute procedure notify_owner_func();


/* funcao para inserir na tabela auction_bakcup uma versao nova de um leilao */
create or replace function create_auction_bak_func() returns trigger
language plpgsql
as $$
begin 
    insert into auction_backup(auction_id, title, description, date_start, date_end, price_min, user_id, version)
    values(new.auction_id, new.title, new.description, new.date_start, new.date_end, new.price_min, new.user_id, new.version);
    return new;
end;
$$;


/* trigger chamado sempre que ocorre uma edicao num leilao */
create trigger create_auction_bak
after UPDATE on auction
for each row
execute procedure create_auction_bak_func();

/* Insere dados nas tabelas */
INSERT INTO auction_user(username, password, email) VALUES('simao', 'pass1234', 'simao@gmail.com');
INSERT INTO auction_user(username, password, email) VALUES('pedro', 'pass1234', 'pedro@gmail.com');
INSERT INTO auction_user(username, password, email) VALUES('joao', 'pass1234', 'joao@gmail.com');
INSERT INTO auction_user(username, password, email) VALUES('miguel', 'pass1234', 'miguel@gmail.com');
INSERT INTO auction_user(username, password, email) VALUES('mickael', 'pass1234', 'mickael@gmail.com');
INSERT INTO auction_user(username, password, email) VALUES('luis', 'pass1234', 'luis@gmail.com');
INSERT INTO auction_user(username, password, email) VALUES('maria', 'pass1234', 'maria@gmail.com');
/*
INSERT INTO auction(title, description, ean_code, date_start, date_end, price_min, seller_id) VALUES('portatil', 'descricao', '12314123', '20210527 20:00 GMT', '20210527 22:00 GMT', 100, 1);
INSERT INTO auction_msg(date, message, username, auction_id) VALUES('20210527 21:00 GMT', 'OLAAAA', 1, 1);
INSERT INTO bids('20210527 21:00 GMT', 101, 1, 1);*/