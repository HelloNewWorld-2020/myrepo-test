import json
import psycopg2
import os
import boto3
    
def lambda_handler(event, context):
    try:
       con = psycopg2.connect(dbname=os.environ["DB_NAME"],
                                 user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
                                 host=os.environ["DB_ENDPOINT"], port=os.environ["DB_PORT"])
    except:
       raise Exception("Server error: cannot connect to database")

    if 'queryStringParameters' in event and event['queryStringParameters']:
        username = event['queryStringParameters']['username']
        User_ID = get_user_id(con, username)
        with con.cursor() as db:
            selectQuery = ('SELECT "Sample_ID", "Confidence_Interval", "Regression_Value", "Create_Time" FROM "Results" where "User_ID" = \'{0}\'').format(User_ID)
            try:
                db.execute(selectQuery)
                results = []
                columns = ("Sample_ID", "Confidence_Interval", "Regression_Value", "Create_Time", "Sample_Name", "Sample_Category", "EEMPlot_URL")
                for row in (db.fetchall()):
                    row = list(row)
                    sample_info = get_sample_info(con, row[0])
                    sample_info = list(sample_info)
                    row.extend(sample_info)
                    print(row)
                    result = map(str, row)
                    #result = list(result)
                    results.append(dict(zip(columns, result)))
                con.commit()
                
                result = json.dumps(results)
            except Exception as e:
                raise Exception("Server error: error inserting to db", e)
    
        #
        # db.close()
        # con.close()
    
        return {
            "statusCode": 200,
            "headers": {
                "accepted":"Send OK"
            },
            "body": result,
            "isBase64Encoded": False
        }
    else:
        return {
            "statusCode": 400,
            "headers": {
                "accepted":"Send OK"
            },
            "body": "No parameter ",
            "isBase64Encoded": False
        }

def get_user_id(con, username):
     with con.cursor() as db:

        selectUserQuery = ('Select "User_ID" From "Users" Where "Name" = \'{0}\'').format(username)
        
        try:

            db.execute(selectUserQuery)
            
            return db.fetchone()[0]

            con.commit()

        except Exception as e:

            raise Exception("Server error: error select User_ID from Users", e)
            
def get_sample_info(con, Sample_ID):
     with con.cursor() as db:

        selectUserQuery = ('Select "Sample_Name", "Sample_Category", "EEMPlot_URL" From "Samples" Where "Sample_ID" = \'{0}\'').format(Sample_ID)
        
        try:

            db.execute(selectUserQuery)
            
            return db.fetchone()
            
            con.commit()

        except Exception as e:

            raise Exception("Server error: error select User_ID from Users", e)