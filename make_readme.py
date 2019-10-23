import gspread
from oauth2client.service_account import ServiceAccountCredentials
import argparse
import sys
import pandas as pd
import datetime
import jinja2



def pandas_df_to_markdown_table(df):
    from IPython.display import Markdown, display
    fmt = ['---' for i in range(len(df.columns))]
    df_fmt = pd.DataFrame([fmt], columns=df.columns)
    df_formatted = pd.concat([df_fmt, df])
    return df_formatted.to_csv(sep="|", index=False)

def link_to_markdown(url, label="link"):
    if not url:
        return None
    return f"[{label}]({url})"

def slides_link(url):
    return link_to_markdown(url, label="slides")

def video_link(url):
    return link_to_markdown(url, label="video")

def main():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open_by_key("1-g5s00HZbmamy2Rr_kb45fZ2zQCls-g-MEEL8kDnzBI").sheet1

    # Extract and print all of the values
    list_of_values = sheet.get_all_values()
    df = pd.DataFrame(list_of_values[1:], columns=list_of_values[0])

    df2 = df[["Title", "Format", "Time (min)", "Date", "Venue", "City", "Country", "Slides", "Video"]]
    df2["Slides"] = df2["Slides"].map(slides_link)
    df2["Video"] = df2["Video"].map(video_link)

    df2 = df2.iloc[::-1] # reverse row order

    # If date is in future, make that row italic
    for i in range(df2.shape[0]):
        date_parsed = datetime.datetime.strptime(df2["Date"].iloc[i], '%d.%m.%Y')
        if date_parsed > datetime.datetime.now():
            for col_idx in range(df2.shape[1]):
                if df2.iloc[i, col_idx]:
                    df2.iloc[i, col_idx] = f"_{df2.iloc[i, col_idx]}_"
        else:
            break

    table_str = pandas_df_to_markdown_table(df2)


    # Put together final doc
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "README.md.template"
    template = templateEnv.get_template(TEMPLATE_FILE)

    with open("README.md", "w") as f:
        f.write(template.render(table=table_str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Make README from Google sheet.")
    args = parser.parse_args(sys.argv[1:])

    if len(sys.argv) < 1:
        parser.print_help()
        exit()

    main()




