from datetime import datetime, timedelta, timezone


class JobFilterService:


    def filter_recent(self, jobs, days=7):

        limit_date = datetime.now(
            timezone.utc
        ) - timedelta(days=days)


        filtered = []


        for job in jobs:

            if not job.published_at:
                continue


            if job.published_at >= limit_date:
                filtered.append(job)


        return filtered