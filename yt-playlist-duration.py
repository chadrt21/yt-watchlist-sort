from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
import csv
from tabulate import tabulate

new_playlist = []

# import data from Watch later.cvs (exported from Google Takeout)
playlist = []
with open('Watch later.csv') as csvfile:
    reader = csv.reader(csvfile)
    c = 0
    for l in reader:
        # ignore the first 4 entries
        if(c >= 4):
            if(len(l) >= 1):
                playlist.append(l[0])
        c += 1


# extract video duration for each video
# https://www.thepythoncode.com/article/get-youtube-data-python
store = open('yt-watchlist-temp.csv','w')
csv_writer = csv.writer(store)
for i in tqdm(range(100)):
    video_url = "https://www.youtube.com/watch?v=" + playlist[i]
    session = HTMLSession()
    response = session.get(video_url)
    response.html.render()
    # running render a second time to bypass the ads which show incorrect video duration
    response.html.render()
    soup = bs(response.html.html, "html.parser")
    # get the video duration
    duration = soup.find("span", {"class": "ytp-time-duration"}).text
    # get the video title
    title = soup.find("meta", itemprop="name")["content"]
    video_link = '<a href="' + video_url + '">' + title + '</a>'
    # convert duration into seconds and add to new_playlist with video link
    new_playlist.append([video_link, duration, sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(duration.split(":"))))])
    csv_writer.writerow([video_link, duration, sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(duration.split(":"))))])

store.close()

# sort videos by duration
sort_playlist = sorted(new_playlist,key=lambda l:l[2])

# export to html with link
with open('new_playlist.html', 'w') as new_html:
    # NOTE: unable to have escape HTML character when using tabulate() causing no hyperlinks
    # new_html.write(tabulate(sort_playlist, ['Video','Duration (sec)'], tablefmt='html'))

    # Alternate color scheme for table
    new_html.write("<!DOCTYPE html>\n")
    new_html.write("<html>\n")
    new_html.write("<head>\n")
    new_html.write("<style>\n")
    new_html.write("table {\n   border-collapse: collapse;\n}\n")
    new_html.write("th, td {\n  text-align: left;\n  padding: 8px;\n}\n")
    new_html.write("tr:nth-child(even) {background-color: #f2f2f2;}\n</style>\n</head>\n<body>\n")

    new_html.write("<table>\n")
    new_html.write("<thead>\n")
    new_html.write("<tr><th>Video                                                                                                                           </th><th style=\"text-align: right;\">  Duration</th><th style=\"text-align: right;\">  Seconds</th></tr>\n")
    new_html.write("</thead>\n")
    new_html.write("<tbody>\n")
    for i in sort_playlist:
        new_html.write("<tr><td>" + i[0] + "</td><td style=\"text-align: right;\">" + str(i[1]) + "</td><td style=\"text-align: right;\">" + str(i[2]) +  "</td></tr>\n")
    new_html.write("</tbody>\n")
    new_html.write("</table>\n")

# export to new csv file?
# with open('new_playlist.csv', 'w') as new_csv:
#     writer = csv.writer(new_csv)
#     for i in new_playlist:
#         writer.writerow(i)
