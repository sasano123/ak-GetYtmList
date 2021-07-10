import os
import datetime
import psycopg2
import smtplib, ssl
from email.mime.text import MIMEText
from apiclient.discovery import build

def main():
    conn_string = os.environ["DATABASE_CONN_INFO"]
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    #datetime---
    dt_now = datetime.datetime.now()
    y2dTime = str(dt_now.strftime("%Y-%m-%d"))
    #---get---
    api_key = os.environ["YOUTUBE_API"]
    youtube = build("youtube", "v3", developerKey=api_key)
    search_response = youtube.playlistItems().list(
        playlistId=os.environ["PLAYLIST_ID"], 
        part="snippet", 
        maxResults=50
        ).execute()
    
    forMailStr = ""
    for i in search_response["items"]:
        title = i["snippet"]["title"].replace("'", "`")
        artist = i["snippet"]["videoOwnerChannelTitle"].replace(" - Topic", "").replace("'", "`")
        after = i["snippet"]["description"].split("\n")
        album = after[4].replace("'", "`")
        #DB
        sql = """INSERT INTO songs(date, title, artist, album) 
        VALUES('{}', '{}', '{}', '{}');""".format(y2dTime, title, artist, album)
        cur.execute(sql)
        conn.commit()
        
        forMailStr += '''
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>
        '''.format(title, artist, album)
    cur.close()
    conn.close()
   
    gmail_account = os.environ["FROM_MAIL_USERNAME"]
    gmail_password = os.environ["FROM_MAIL_PASS"]
    mail_to = os.environ["TO_MAIL_USERNAME"]
    mailHead = '''
    <div>
        <p>
            プレイリスト<b>「favs4app」</b>を取得しました。
        </p>
        <p>
            {}
        </p>
        <a href="https://showytmlistdb.herokuapp.com/index.php">
            データベース閲覧
        </a>
    </div>
    '''.format(y2dTime)
    resultTable = '''<br>
    <table border="1">
        <tr>
            <th>Title</th>
            <th>Artist</th>
            <th>Album</th>
        </tr>
        {}
    </table>'''.format(forMailStr)

    subject = "YTMlist.pyの結果 " + y2dTime
    body = mailHead +  resultTable
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["To"] = mail_to
    msg["From"] = gmail_account

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
    context=ssl.create_default_context())
    server.login(gmail_account, gmail_password)
    server.send_message(msg) # メールの送信
    
    return body
    
    
if __name__ == "__main__":
    main()
    
        







