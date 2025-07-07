# system
import os
from dotenv import load_dotenv
# local
from ..models.general import Video
# third-party
from googleapiclient.discovery import Resource, build # client for using all youtube search services

load_dotenv()


# function for getting snippet and other basic information
# given video id and v3 build/client
# NOTE: Should also be able to handle a list if it's not too weird
# When using, have a batch limit on the video id's 
# to avoid passing the GET request url character limit
def get_basic_info(client: Resource, videoId: list[str] | str) -> list[Video] | Video:
    # NOTE: Cases/conditions
    # - handle list of strings
    # - handle single string

    # Use the client to fetch video informaiton for one video Id
    response = client.videos().list(
        part='snippet',
        id=videoId
    ).execute()

    meta = Video(
        id=videoId, title=response['items'][0]['snippet']['title'],
        description=response['items'][0]['snippet']['description'],
        uploaded_at=response['items'][0]['snippet']['publishedAt'],
    )

    # NOTE: review and update the above function to handle multiple videos
    # when given a list of video id's instead of a single video 
    return meta



if __name__=="__main__":
    # initialize a sample list of video Id's to
    # use from the actual database for fetching snippet info
    videoIds: list[str] = ['w4wRyFOBhSQ', 'HwXpRSdk0zs', 'vYEMu_8pX8k', '221sEEibeZA', 'Hq5uO8B7VY8', 'uaePRgNSg2c', '0iXYmthHzxo', 
                'NIdyh9bpgPw', 'TtW8rFcxe1k', '80y0o5fMEKA', 'l39X7dFNEoo', 'Ray7HasqB8Y', 'uwaXoOJgcoo', 'ma1Y9ZnY69g', 
                'P0TBivVYbdc', 'btie26UA1LI', 'OVpQiNNBP9k', 'jbxv4EIcRlE', 'SYel-mVSMAI', '-HD4FBlMO_8', 'q2ClNZxsKG8', 
                'Z5SQYaD9Au4', 'lHlE6dfbt4s', 'B59gdVynAsU', 'Ub29Pp1BcUI', 'DhXIrg5f8Qk', '09WKJb8adxw', 'YA0VjgaAieY', 
                'IUVC-5e0uoY', 'r8-0AXieQnY', 'DrUoYfM2a2w', 'PuxZH48Zbpo', 'V_ZTtua214I', '6926_H4aAQs', 'DdUiz9nYrV8', 
                'XTtEMlnCPkc', 'x5qtUXWwSgQ', '5bvpwiyJtVk', 'P_6D-e7thf4', 'qo1hCWwhRHk', 'UJiI9aRcsFY', '9Ot2d0A_edU', 
                'L56ziyAHjFg', 'F5z8oxAidAM', 'jLmwhsUREC4', 'DFXdqByRxNg', 'P25bCB5DJNw', 'QhdgSrUweiE', 'aa0aOAzTliM', 
                'vRYzR_msQLA', 'ZfP5DdLPpA0', 'ZMgdLCEqTHU', 'ZYsGAXHOerg', 'E_eO8O1KV9Y', 'woK3LLuQdgE', 'DdxZUrcfqbk', 
                'NGTNgI0StWw', 'P11KnOSi5Bw', 'mqy3ymYcE_s', 'tJ1_r4S49Oc', 'mrDaMfx2e5E', 'KneBgPTff2w', 'U9PlYbmEWOk', 
                'HmhygE84EPQ', 'mVkKOPNGvjA', 'PA3PJDLNwFU', 'U3bBzQJQ9Tk', 'aEqTjrSomAk', 'c9gTpk-tz5w', 'OraT730YtJQ', 
                'vqZuqBCu5g0', 'pgVlWxMMJmw', '6lJp0hmRVr0', 'XupvhKEF-_w', 'BBmMlux7mhk', '7XYIhkBy0Mk', 'TVS4VG_x_Tc',
                'v7jSvlG_CUM', 'PV2f50-O7N4', 'QBqwipFt0Ww', 'ALEeReC3u5Y', 'bwqH6ej7nS0', 'qBzgQcdOJWk', 'n6EUwvCkWJ8',
                'ERjxnV3KqlE', 'sQ3hQlRKMi4', 'b4Ll1ek3VS0', '-8NmNnAJwdc', 'BO4y_JUO0hQ', 'rTUFu5VJQYw', '9kKiMN7jEQw', 
                'mNkTeok_dE0', 'Cr767ioThuk', 'udwTXwE3ePE', '4VXHgblxa_U', 'BWitv9AKoNU', 'wTdmQ_eL42o', '69_vxa-x2gs', 
                'zeXr5MYN6RQ', 'Q7UxljP17cw', 'FmvDMTfiJR4', 'NythsT2GH5Y', 'C5vPHu321Nw', 'eyJ7zQ15Gys', 'Sqj3U3SuHH8', 
                'YH1zfI7Sa54', 'Dpbwvhh0cZ8', 'w0bZs2RPKM4', 'E8x1Cva8hJ8', '9cZ93q7rqcc', 'OF9GZNU0eQc', 'WA80-USZ_UI', 
                '4HBVdF5AXc0', 'PCWbmiFE4Rg', 'GwYL0ytoiso', '_5V8RJjCLgE', 'Y8qDejEyTaI', '4wcAbxhQYZo', 'QsUFU2faWqg', 
                'kjNODeSVgYQ', 'BcxFDZNUMcM', 'iByvUzTk4Ko', 'u9BKVr5FuCg', 'DMUuThQPX4M', 'J725uTMRtgU', 'ra0tIjxI2Tc', 
                'kZqwSqfBlSg', 'WwWOwUi1Lps', 'GshEzcqlUbY', '3-BAtCgPZws', 'CnQcCKjqiic', 'vqh00mL-ggw', 'LpZX-uD46pQ', 
                'swlxiSMHjZU', '9gIKeNW5P-c', 'Pzn_zCCkVLI', 'UGp6VzbkReA', 'Yd7XlToHvhI', 'Jd5-QbSyHAs', 'kbM493l48yU', 
                'YnEmxz55AF0', '74bvSlFl0BM', 'dMne1Rz2tks', '2IA8oJd8B4Y', 'Zwh6ArgcHZE', 'cQFxNq-Jpf0', 'gMGRrzsl4Yc', 
                'H3gIH-k5WXw', 'Ua7vM0ESIK8', 'jkd_RTFfVyY', 'ZNoIaoyU6zk', 'NhYJPPT9rcY', 'OoL2Bo5xAaM', 'WKcdJ8i5HcE', 
                'KviW1C-OVIg', 'oa-GPurs8Vw', 'SluJ8m4ADk8', 's_d2QYt3zzw', '8s2hnvhZgqU', '4UebSzZOLno', 'HAo9-GV8-pM', 
                'wuVD-iXnR9c', 'hgCXDugxHjc', 'mBmDD8MU4cI', 'UvKM3k0fbMc', 'RKTq5CgsF9I', '2BDNE9Ci26I', 'V_b0c4dMqhY', 
                'bOJ2txGsZxQ', 'Apiijl8_Jm4', 'mlrAfg3aYtA', 'hCxlussP7Bg', 'nYnJ_DKqRac', 'udexDY1WKSc', '6MeiKSZEFT4', 
                'WVOXKrJlU2U', 'gKhKdswn2pQ', '3pA9wI7TtJ4', 'WqXwqNlPydY', 'Tn12-fMKLhk', 'ZS-23JCbiBs']


    # Initialize youtube data api client for fetching data
    # build's HTTP layer/closing is taken care by the package
    client: Resource = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE'))
 
    # NOTE: call the get_basic_info function which returns an extracted response
    # or throws an error since this is a backend type funtion
    # or we can leave the deconstruction to be done out here
    response: Video = get_basic_info(client, videoId=videoIds[0])
    print(response)