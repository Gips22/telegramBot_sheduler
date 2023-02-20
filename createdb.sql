create table if not exists task (
        id integer primary key autoincrement,
        task_name varchar(500),
        completed boolean default false,
        created datetime default current_timestamp,
        user_task integer,
        foreign key(user_task) references person(id)
    );


create table if not exists person(
    id integer primary key autoincrement,
    username varchar(255),
    tg_id integer(255)
);