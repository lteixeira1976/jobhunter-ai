import requests


class JobDetailService:


    def get_description(self, url):

        try:

            response = requests.get(url)

            if response.status_code != 200:
                return ""

            data = response.text

            return data.lower()


        except Exception:

            return ""