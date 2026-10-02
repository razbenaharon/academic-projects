
from django.shortcuts import render
from django.db import connection
from . import models


# Create your views here.

def dictfetchall(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def index(request):
    return render(request, 'index.html')


def QueryResults(request):
    with connection.cursor() as cursor:
        # Query1
        cursor.execute(
            """
            SELECT DISTINCT I.Name, TS.TotalSum
            FROM CountSector CS, TotalSum TS, Investor I
            WHERE CS.ID = TS.ID and CS.ID = I.ID and TS.ID = I.ID
            ORDER BY TS.TotalSum DESC
            """
        )
        sql_res1 = dictfetchall(cursor)

    with connection.cursor() as cursor:
        # Query2
        cursor.execute(
            """SELECT H.Symbol, H.Name, H.Quantity
                FROM
                
                (SELECT Symbol,Name, SUM(BQuantity) as Quantity
                FROM
                (SELECT OS.Symbol,I.Name, B.BQuantity
                FROM OneSector OS, Buying B, Investor I
                WHERE OS.Symbol = B.Symbol and B.ID = I.ID) AS G
                GROUP BY Symbol, Name) as H
                
                LEFT JOIN
                
                (SELECT Symbol,Name, SUM(BQuantity) as sQuantity
                FROM
                (SELECT OS.Symbol,I.Name, B.BQuantity
                FROM OneSector OS, Buying B, Investor I
                WHERE OS.Symbol = B.Symbol and B.ID = I.ID) AS G
                GROUP BY Symbol, Name) as H1 on H.Symbol = H1.Symbol and
                                                  H.Quantity < H1.sQuantity
                WHERE (H1.Symbol IS NULL) and (H1.Name IS NULL )
                ORDER BY H.Symbol, H.Name"""
        )
        sql_res2 = dictfetchall(cursor)

    with connection.cursor() as cursor:
        # Query3
        cursor.execute(
            """select RelevantCompany.Symbol, ISNULL(NumOfBuy, 0) as NumOfBuy
               from RelevantCompany
               left join FirstDayBuy on RelevantCompany.Symbol=FirstDayBuy.Symbol 
               order by RelevantCompany.Symbol
            """
        )
        sql_res3 = dictfetchall(cursor)

    return render(request, 'QueryResults.html', {'sql_res1': sql_res1, 'sql_res2': sql_res2, 'sql_res3': sql_res3})


def AddTransaction(request):
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT TOP 10 T.tDate, T.ID, T.TAmount
               FROM Transactions T
               ORDER BY T.tDate DESC, T.ID DESC
            """
        )
        sql_res4 = dictfetchall(cursor)

        if request.method == 'POST' and request.POST:

            new_ID = request.POST["ID"]
            new_TransSum = request.POST["TransactionSum"]

            cursor.execute(
                """
                SELECT MAX(S.tDate)
                FROM Stock S
                """
            )
            new_tdate = dictfetchall(cursor)
            new_tdate = new_tdate[0]['']

            if not models.Investor.objects.filter(id=new_ID).exists():
                message = f" Investor ID does not exist in the Database"
                return render(request, 'AddTransaction.html', {'message': message, 'sql_res4': sql_res4})

            if models.Transactions.objects.filter(id=new_ID, tdate=new_tdate).exists():
                message = f"Oops, you've already made a transfer today"
                return render(request, 'AddTransaction.html', {'message': message, 'sql_res4': sql_res4})

            cursor = connection.cursor()
            query = "INSERT INTO Transactions(tdate, id,tamount) VALUES (%s, %s,%s)"
            values = (str(new_tdate), str(new_ID), str(new_TransSum))
            cursor.execute(query, values)
            connection.commit()

            investor_ID = models.Investor.objects.get(id=new_ID)
            new_amount = str(float(investor_ID.amount) + float(new_TransSum))
            investor_ID.amount = new_amount
            investor_ID.save()

            cursor.execute(
                """
                SELECT TOP 10 T.tDate, T.ID, T.TAmount
                FROM Transactions T
                ORDER BY T.tDate DESC, T.ID DESC
                """
            )
            sql_res4 = dictfetchall(cursor)

            return render(request, 'AddTransaction.html', {'sql_res4': sql_res4})

    return render(request, 'AddTransaction.html', {'sql_res4': sql_res4})


def BuyStocks(request):
    with connection.cursor() as cursor:
        # Query5
        cursor.execute(
            """
                SELECT TOP 10 B.tDate, B.ID, B.Symbol, B.BQuantity
                FROM Buying B
                ORDER BY B.tDate DESC, B.ID DESC, B.Symbol
                """
        )
        sql_res5 = dictfetchall(cursor)

        if request.method == 'POST' and request.POST:

            new_ID = request.POST["ID"]
            new_Company = request.POST["Company"]
            new_Quantity = request.POST["Quantity"]

            cursor.execute(
                """
                SELECT MAX(S.tDate)
                FROM Stock S
                WHERE S.Symbol = %s;
                """,
                (new_Company,)
            )
            new_tdate = dictfetchall(cursor)
            new_tdate = new_tdate[0]['']

            if (not models.Investor.objects.filter(id=new_ID).exists()) and (not models.Company.objects.filter(symbol=new_Company).exists()):
                message = "-Investor ID does not exist in the Database -Symbol Company does not exist in the Database"
                return render(request, 'BuyStocks.html', {'message': message, 'sql_res5': sql_res5})
            if not models.Investor.objects.filter(id=new_ID).exists():
                message = f" Investor ID does not exist in the Database"
                return render(request, 'BuyStocks.html', {'message': message, 'sql_res5': sql_res5})
            if not models.Company.objects.filter(symbol=new_Company).exists():
                message = f" Symbol Company does not exist in the Database"
                return render(request, 'BuyStocks.html', {'message': message, 'sql_res5': sql_res5})

            symbolNew_tdate = models.Stock.objects.get(symbol=new_Company, tdate=new_tdate)
            stock_price = float(symbolNew_tdate.price)
            investor_ID = models.Investor.objects.get(id=new_ID)
            amount = float(investor_ID.amount)
            new_Quantityf = float(new_Quantity)

            if (stock_price * new_Quantityf) > amount and models.Buying.objects.filter(id=new_ID, tdate=new_tdate, symbol=new_Company).exists():
                message = "-The purchase cost is greater than the amount of money you have    -You already bought from this company today"
                return render(request, 'BuyStocks.html', {'message': message, 'sql_res5': sql_res5})

            if (stock_price * new_Quantityf) > amount:
                message = "The purchase cost is greater than the amount of money you have"
                return render(request, 'BuyStocks.html', {'message': message, 'sql_res5': sql_res5})

            if models.Buying.objects.filter(id=new_ID, tdate=new_tdate, symbol=new_Company).exists():
                message = f"Oops, you already bought from this company today"
                return render(request, 'BuyStocks.html', {'message': message, 'sql_res5': sql_res5})

            new_amount = amount - stock_price * new_Quantityf
            investor_ID.amount = new_amount
            investor_ID.save()

            cursor = connection.cursor()
            query = "INSERT INTO Buying(tdate,id,symbol,bquantity) VALUES (%s, %s,%s,%s)"
            values = (str(new_tdate), str(new_ID), str(new_Company), str(new_Quantity))
            cursor.execute(query, values)
            connection.commit()

            cursor.execute(
                """    
                SELECT TOP 10 B.tDate, B.ID, B.Symbol, B.BQuantity
                FROM Buying B
                ORDER BY B.tDate DESC, B.ID DESC, B.Symbol
                """
            )
            sql_res5 = dictfetchall(cursor)
            return render(request, 'BuyStocks.html', {'sql_res5': sql_res5})
    return render(request, 'BuyStocks.html', {'sql_res5': sql_res5})
