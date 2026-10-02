CREATE VIEW BuyingSymbol
AS
SELECT B.tDate, B.ID, B.Symbol, S.Price, B.BQuantity
FROM Buying B LEFT JOIN Stock S on B.Symbol = S.Symbol and S.tDate = B.tDate;


CREATE VIEW CountSector
AS
SELECT  BS.ID, BS.tDate, COUNT(DISTINCT C.Sector) as CountSec
FROM BuyingSymbol BS LEFT JOIN Company C on BS.Symbol = C.Symbol
GROUP BY BS.tDate, BS.ID
HAVING COUNT(DISTINCT C.Sector) >= 6;


CREATE VIEW TotalSum
As
SELECT BS.ID, ROUND(SUM(BS.Price*BS.BQuantity), 3) as TotalSum
FROM BuyingSymbol BS
GROUP BY BS.ID;


CREATE VIEW SymbolDate
AS
SELECT DISTINCT B.Symbol,B.tDate
FROM Buying B
GROUP BY B.Symbol, B.tDate;


CREATE VIEW CountSymbol
AS
SELECT A.Symbol, SUM(A.CountSymb1) as CountSymb
FROM
    (SELECT SD.Symbol, COUNT(SD.Symbol) as CountSymb1
    FROM SymbolDate SD
    GROUP BY SD.tDate, SD.Symbol) as A
GROUP BY A.Symbol;


CREATE VIEW AllSymbol
AS
SELECT CS.Symbol, CS.CountSymb, C.Sector
FROM CountSymbol CS LEFT JOIN Company C on CS.Symbol = C.Symbol
WHERE CS.CountSymb IN (
                   SELECT COUNT(DISTINCT B1.tDate)
                   FROM Buying B1);


CREATE VIEW OneSector
AS
SELECT ASL.Symbol, ASL.Sector
FROM AllSymbol ASL
WHERE ASL.Sector IN (
    SELECT F.Sector
    FROM AllSymbol F
    GROUP BY F.Sector
    HAVING COUNT(F.Sector) = 1);


create view RelevantCompany as
    SELECT Symbol
    FROM (select first.Symbol,min_date,first.Price as pmin,max_date,last.Price as pmax
from (SELECT Symbol, min_date ,Price
FROM stock s
LEFT JOIN (
    SELECT MIN(tDate) AS min_date
    FROM stock
) min_date ON s.tDate = min_date
where min_date is not null)as first
left join (
    SELECT Symbol, max_date ,Price
FROM stock s
LEFT JOIN (
    SELECT MAX(tDate) AS max_date
    FROM stock
) min_date ON s.tDate = max_date
where max_date is not null
)as last on last.Symbol=first.Symbol)as first_and_last
    WHERE pmax > 1.06 * first_and_last.pmin;


create view FirstDayBuy as
select Symbol, count(*) as NumOfBuy
from buying b
LEFT JOIN (
    SELECT MIN(tDate) AS min_date
    FROM stock
) min_date ON b.tDate = min_date
where min_date is not null
group by Symbol;





