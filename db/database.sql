-- Library Database Application
-- Author: Milana Poljanskova
-- Contact: mila.p.06@seznam.cz

begin transaction;

create database library;
use library;

create table author (
id int primary key identity(1,1),
surname varchar(50) not null,
name varchar(50) not null,
email varchar(200) unique,
is_active bit not null default 1
);

create table publisher (
id int primary key identity(1,1),
name varchar(50) not null,
address varchar(200),
phone_number varchar(30),
email varchar(200),
website varchar(200)
);

create table book (
id int primary key identity(1,1),
name varchar(50) not null,
publisher int not null,
publishment_date date,
rating float,
binding varchar(20) not null,
foreign key (publisher) references publisher(id),
check (binding in ('hardcover', 'paperback', 'ebook'))
);

create table book_author (
id int primary key identity(1,1),
author_id int not null,
book_id int not null,
is_active bit default 1,
foreign key (author_id) references author(id),
foreign key (book_id) references book(id)
);

create table genre (
id int primary key identity(1,1),
name varchar(50) not null
);

insert into book (name, publisher, publishment_date, rating, binding)
values
('Python Basics', 1, '2022-01-15', 4.5, 'hardcover'),
('Advanced SQL', 2, '2021-09-10', 4.0, 'paperback'),
('Data Science Handbook', 1, '2020-05-20', 4.8, 'ebook');

insert into book_author (author_id, book_id, is_active)
values
(1, 3, 1),
(2, 4, 1),
(1, 5, 1),
(3, 3, 1);

create or alter view vw_book_list as
select
    b.id as book_id,
    b.name as book_name,
    p.name as publisher_name,
    b.publishment_date,
    b.rating,
    b.binding
from book b
join publisher p on p.id = b.publisher;

create or alter view vw_publisher_report as
select
    p.id as publisher_id,
    p.name as publisher_name,
    count(distinct b.id) as books_count,
    avg(b.rating) as avg_rating,
    count(distinct ba.author_id) as active_authors
from publisher p
left join book b on b.publisher = p.id
left join book_author ba on ba.book_id = b.id and ba.is_active = 1
group by p.id, p.name;


commit;
