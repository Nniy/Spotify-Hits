from datetime import date, timedelta
import pandas as pd
import requests
from tqdm import tqdm
import glob
import argparse
import os
import errno


def mkdir(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def get_spotify_hit_songs(start, end, region):
    s = [int(x) for x in start.split("-")]
    e = [int(x) for x in end.split("-")]
    prefix = "https://spotifycharts.com/regional/"
    start_date = date(s[0], s[1], s[2])
    end_date = date(e[0], e[1], e[2])
    assert end_date >= start_date
    delta = end_date - start_date
    for i in tqdm(range(delta.days + 1)):
        day = start_date + timedelta(days=i)
        day_string = day.strftime("%Y-%m-%d")
        url = prefix + region + "/daily/" + day_string + "/download"
        res = requests.get(url, allow_redirects=True)
        if res.status_code != 404:
            filepath = f'./{region}/{day_string}.csv'
            mkdir(filepath)
            open(filepath, 'wb').write(res.content)
        else:
            print(f'File not available on date {day_string}')

    all_files = glob.glob(f"./{region}/*.csv")
    df = pd.concat((pd.read_csv(f, skiprows=1) for f in all_files))
    result = df.groupby(by=["Track Name", "Artist"]).Streams.sum().reset_index()
    result.sort_values(by="Streams", ascending=False).to_csv("hit_songs.csv", index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=str)
    parser.add_argument('--end', type=str)
    parser.add_argument('--region', type=str, choices=['us', 'gb', 'global'])
    args = parser.parse_args()
    get_spotify_hit_songs(args.start, args.end, args.region)
