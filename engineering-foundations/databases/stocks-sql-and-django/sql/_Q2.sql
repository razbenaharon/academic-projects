
CREATE TABLE Company(
    symbol VARCHAR(40) PRIMARY KEY ,
    sector VARCHAR(40),
    founded INT,
    cLocation VARCHAR(40),
)

CREATE TABLE Investor(
    iId INT PRIMARY KEY ,
    iName VARCHAR(40) NOT NULL ,
    iEmail VARCHAR(40) NOT NULL UNIQUE,
    birthDate DATE,
    registerDate DATE,
    check(iId between 100000000 and 999999999),
    check (YEAR(birthDate) < 2006)
)

CREATE TABLE Beginner
(
    bId INT PRIMARY KEY ,
    FOREIGN KEY (bId) REFERENCES Investor(iId)
)

CREATE TABLE Premium(
    pId INT PRIMARY KEY,
    financialGoal VARCHAR(40),
    FOREIGN KEY (pId) REFERENCES Investor(iId)
)
--We cannot check at the DDL level that:
--A new investor who starts using the company's services is defined in the first three
--months after his registration as a beginner investor,
--then he becomes a premium investor.

CREATE TABLE Worker(
    wId INT PRIMARY KEY,
    FOREIGN KEY (wId) REFERENCES Premium(pId)
)

CREATE TABLE GuidedBy(
    wId INT,
    bId INT UNIQUE,
    FOREIGN KEY (wId) REFERENCES Worker(wId),
    FOREIGN KEY (bId) REFERENCES Beginner(bId),
    PRIMARY KEY (wId, bId)
    )

--We cannot check at the ddl level that:
--Each employee has at least one beginner investor whom he guides.


CREATE TABLE InRivalry(
    company1 VARCHAR(40),
    company2 VARCHAR(40),
    reason VARCHAR(40),
    check (company1 != company2),
    check (company1 > company2),
    PRIMARY KEY (company1,company2),
    FOREIGN KEY (company1) REFERENCES Company(symbol),
    FOREIGN KEY (company2) REFERENCES Company(symbol),
)

CREATE TABLE Follow(
    company1 VARCHAR(40),
    company2 VARCHAR(40),
    wId INT UNIQUE,
    report VARCHAR(40),
    FOREIGN KEY (company1,company2) REFERENCES InRivalry(company1, company2),
    FOREIGN KEY (wId) REFERENCES Worker(wId),
    PRIMARY KEY (company1,company2)
)

CREATE TABLE TradingAccount(
    accountId VARCHAR(40) PRIMARY KEY,
    iId INT,
    tMoneyAvailable FLOAT,
    check (len(accountId)=10),
    FOREIGN KEY (iId) REFERENCES Investor(iId),
)

--The tMoneyAvailable field should change every time a purchase was made or when a certain amount
--of money was transferred to the account.But we can't update it at ddl level.

CREATE TABLE Stock(
    sValue FLOAT,
    sDate DATE,
    symbol VARCHAR(40),
    FOREIGN KEY (symbol) REFERENCES Company(symbol),
    PRIMARY KEY (sDate, symbol)
)

--We cannot check at the ddl level that:
--For each of the companies listed in the database there is a record of at least
--one stock on any given day.

CREATE TABLE Buying(
    sDate DATE,
    symbol VARCHAR(40),
    amountOFStocks FLOAT,
    accountId VARCHAR(40),
    FOREIGN KEY (accountId) REFERENCES TradingAccount (accountId),
    FOREIGN KEY (sDate,symbol) REFERENCES Stock(sDate,symbol),
    PRIMARY KEY (sDate,symbol,accountId)
)


CREATE TABLE Transactions(
    tDate DATE,
    accountId VARCHAR(40),
    sumMoneyTrans FLOAT,
    CHECK (sumMoneyTrans >= 1000),
    FOREIGN KEY (accountId) REFERENCES TradingAccount(accountId),
    PRIMARY KEY (tDate, accountId),
)


CREATE TABLE ExamineBy(
    accountId VARCHAR(40),
    tDate DATE,
    wId INT,
    decision BINARY,
    FOREIGN KEY (tDate, accountId) REFERENCES Transactions(tDate, accountId),
    FOREIGN KEY (wId) REFERENCES Worker(wId),
    PRIMARY KEY (tDate, accountId,decision)
)

--We assume that all transfers found in the "Examine"
--table are suspicious transfers
