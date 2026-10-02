
CREATE TABLE Users(
    userId VARCHAR(50),
    userName VARCHAR(8) UNIQUE NOT NULL ,
    userPass VARCHAR(50) NOT NULL,
    userCountry VARCHAR(50) NOT NULL,
    primary key(userId),
    check(len(userName) = 8)
)

CREATE TABLE Content(
    userID  VARCHAR(50),
    cMessage VARCHAR(280) NOT NULL ,
    cDate DATETIME,
    check (len(cMessage) > 0),
    check (YEAR(cDate) > 2019),
    foreign key(userID) references Users(userId),
    primary key(userID, cDate),
)

CREATE TABLE Product(
    pName VARCHAR(50) PRIMARY KEY ,
    pCategory VARCHAR(50),
    pMaxPrice FLOAT,
    check (pCategory is not null),
    check (pMaxPrice is not null),
    check (pMaxPrice > 0),
)

CREATE TABLE ProductSale(
    sellerId VARCHAR(50),
    pName VARCHAR(50),
    pPrice FLOAT DEFAULT 0,
    pCondition VARCHAR(50),
    pUrl VARCHAR(100),
    pSold VARCHAR(1),
    buyerId VARCHAR(50),
    check (pCondition = 'new' or pCondition = 'used' or pCondition = 'fair' or pCondition = 'broken'),
    check (pUrl LIKE '_%.PNG'),
    check (pSold = 't' or pSold = 'f'), --whether the product is sold or not
    check (pPrice >= 0),
    primary key(sellerId, pName),
    foreign key (sellerId) references Users(userId),
    foreign key (pName) references Product(pName),
-- we cant make sure that price is between 0 and pMax Price because it is not primary key in
-- can be different max price for different product unlike the instructions
-- that for each product there is a unique max price
)

CREATE TABLE WrongReport
(
    rDescription  VARCHAR(50),
    rUserIdSend   VARCHAR(50),
    rUserIdReceive VARCHAR(50),
    pName VARCHAR(50),
    rDate  DATETIME,
    vindicatedReport BINARY NOT NULL,
    check (rUserIdReceive != rUserIdSend),
    foreign key (rUserIdReceive) references Users (userId),
    foreign key (rUserIdSend) references Users (userId),
    foreign key (pName) references Product (pName),
    primary key (rUserIdSend, pName, rUserIdReceive, rDate),
    --We can't make sure that a user Can't report more than 2
    --different item postings per day
)