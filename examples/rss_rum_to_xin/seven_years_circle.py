import datetime


class SevenYearsCircle:
    def __init__(self, born_year, born_month, born_day):
        self.born_year = int(born_year)
        self.born_month = int(born_month)
        self.born_day = int(born_day)
        self.birthday = self.circle_begin(0)
        self.this_circle = self.this_circle()

    def circle_begin(self, circle_number=0):
        day = f"{self.born_year + 7*circle_number}-{self.born_month}-{self.born_day}"
        return datetime.datetime.strptime(day, "%Y-%m-%d").date()

    def this_circle(self):

        today = datetime.date.today()
        passed = today - self.birthday
        n = passed.days // (365 * 7)
        m = 0

        for i in range(n - 1, n + 2):
            if self.circle_begin(i) >= today:
                m = i
                break

        this_circle = self.circle_begin(m)
        next_circle = self.circle_begin(m + 1)
        total_days = (next_circle - this_circle).days

        data = {
            "today": str(today),
            "birthday": str(self.birthday),
            "age": 1 + passed.days // 365,
            "passed_days": passed.days,
            "this_circle_number": m,
            "this_circle_begin": str(this_circle),
            "this_circle_passed_days": (today - this_circle).days,
            "this_circle_remain_days": (next_circle - today).days,
            "this_circle_passed_percent": round((today - this_circle).days / total_days, 4),
        }
        return data

    def text_status(self):
        c = self.this_circle
        data = "\n".join(
            [
                f"我出生于 {c['birthday']}，",
                f"迄今 {c['today']}，我正 {c['age']} 岁。",
                "",
                "又或者说，",
                f"我生活在这颗星球上达 {c['passed_days']} 天，",
                f"或 {c['passed_days']*24} 小时，",
                f"或 {c['passed_days']*24*60} 分钟，",
                f"或 {c['passed_days']*24*60*60} 秒……",
                "",
                "七年就是一辈子。",
                f"这是我的第 {c['this_circle_number']} 辈子，",
                f"它开始于 {c['this_circle_begin']}，",
                f"已经过去 {c['this_circle_passed_days']} 天，",
                f"还剩下 {c['this_circle_remain_days']} 天，",
                f"时光流逝 {c['this_circle_passed_percent']*100}%，进度感人……",
            ]
        )
        return data


if __name__ == "__main__":
    text = SevenYearsCircle(1984, 10, 5).text_status()
    print(text)
