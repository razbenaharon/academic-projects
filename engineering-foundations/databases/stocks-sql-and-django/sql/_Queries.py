QUERY_ANSWERS = {
    "Q3":
        """
        SELECT DISTINCT T.ID, C.CountActions AS Actions, T.TotalPrice AS TotalSum, TS.Sector
        FROM TotalSumPrice T, CountOfActions C, MoreThan2 M, TopSector TS
        WHERE T.ID = C.ID and T.ID = M.ID and C.ID = M.ID and TS.ID = T.ID and TS.ID = C.ID
              and TS.ID = M.ID
        GROUP BY T.ID, C.CountActions, T.TotalPrice, TS.Sector
        HAVING COUNT(M.ID)
                   IN (
                   SELECT COUNT(DISTINCT B1.tDate)
                   FROM Buying B1)
        ORDER BY C.CountActions DESC, TS.Sector;
        
        """,
		
	"Q4":
        """
        SELECT  id, count(*) as Actions
        FROM RelevantID
        INNER JOIN (
        SELECT Symbol
        FROM Company
        WHERE Location='California' AND Founded<2000
        ) as company3 on company3.Symbol=RelevantID.Symbol
        group by id

        """
}
