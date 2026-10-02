VIEWS_DICT = {
    "Q3":
        [
		"""
		CREATE VIEW TotalSumPrice
        AS
        SELECT B.ID, ROUND(SUM((Price * BQuantity)), 3) as TotalPrice
        FROM Stock S, Buying B
        WHERE S.Symbol = B.Symbol and S.tDate = B.tDate
        GROUP BY B.ID;


		""",
        """
        CREATE VIEW CountOfActions
        As
        SELECT B.ID, COUNT(B.ID) as CountActions
        FROM Buying B
        GROUP BY B.ID;
                
        """
            ,
        """
        CREATE VIEW MoreThan2
        AS
        SELECT B.ID,B.tDate, COUNT(DISTINCT B.Symbol) as NumOfSymbol
        FROM Buying B
        GROUP BY B.tDate, B.ID
        HAVING COUNT(DISTINCT B.Symbol) >= 2;
        
        """
            ,
        """
        CREATE VIEW CountSector
        AS
        SELECT B.ID,C.Sector,COUNT(C.Sector) AS CountOfSector
        FROM Buying B LEFT JOIN Company C ON B.Symbol = C.Symbol
        GROUP BY B.ID, C.Sector;
        
        """
            ,
        """
        CREATE VIEW TopSector
        As
        SELECT C.ID, C.Sector, C.CountOfSector
        FROM CountSector C
        LEFT JOIN CountSector C1 ON C.ID = C1.ID AND (C.CountOfSector < C1.CountOfSector OR (C.CountOfSector = C1.CountOfSector AND C.Sector > C1.Sector))
        WHERE C1.ID IS NULL;
        
        """
        ]
    ,
    "Q4":
        [
		"""
        CREATE VIEW AllDatesSymbols AS
        SELECT A.Symbol, B.tDate, Stock.Price
        FROM
       (SELECT DISTINCT tDate FROM Stock) B
        LEFT JOIN
       (SELECT DISTINCT Symbol FROM Stock) A
        ON 1=1
        LEFT JOIN Stock ON A.Symbol = Stock.Symbol AND B.tDate = Stock.tDate;

		""",
        """
        CREATE VIEW AllDatesBigger AS
        SELECT Dates.Symbol, Dates.tDate as t1 , Dates.Price as p1, BiggerDates.tDate as t2 , BiggerDates.Price as p2
        FROM AllDatesSymbols as Dates
        left join AllDatesSymbols as BiggerDates on Dates.Symbol= BiggerDates.Symbol
        WHERE Dates.tdate < BiggerDates.tDate;
        
        """
        ,
        """
        CREATE VIEW DayAfter AS
        SELECT AllDatesBigger.Symbol, AllDatesBigger.t1, AllDatesBigger.p1, AllDatesBigger.t2, AllDatesBigger.p2
        FROM AllDatesBigger
        INNER JOIN (
            SELECT Symbol, t1,MIN(t2) as min_t2
            FROM AllDatesBigger
            GROUP BY Symbol, t1
        ) AS min_t2_table ON AllDatesBigger.Symbol = min_t2_table.Symbol
                         AND AllDatesBigger.t1 = min_t2_table.t1
                         AND AllDatesBigger.t2 = min_t2_table.min_t2;
        """
            ,
        """
        CREATE VIEW OneStock AS
        SELECT Buying.Symbol, Buying.tDate
        FROM Buying
        INNER JOIN (
            SELECT B.Symbol
            FROM Buying B
            GROUP BY B.Symbol
            HAVING COUNT(B.Symbol) = 1
        ) AS OneStock ON OneStock.Symbol = Buying.Symbol;
        """
            ,
        """
        CREATE VIEW RelevantID AS
        SELECT Buying.ID,Symbol,BQuantity
        FROM Buying
        inner join (
            SELECT Buying.ID
        FROM Buying
        INNER JOIN (SELECT DayAfter.Symbol
        FROM DayAfter
        INNER JOIN OneStock on DayAfter.Symbol=OneStock.Symbol AND DayAfter.t1=OneStock.tDate
        WHERE (DayAfter.p1*1.02) < DayAfter.p2) as RelevantCompany on RelevantCompany.Symbol=Buying.Symbol
        ) as RelevantID on Buying.ID=RelevantID.ID;
        """
        ]
}



















