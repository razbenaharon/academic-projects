
from mrjob.job import MRJob
from mrjob.step import MRStep

class CompShow(MRJob):

    def contains_letter(self, title):
        letters = ['j', 'q', 'z']
        title_lower = title.lower()
        for letter in letters:
            if letter in title_lower:
                return True
        return False

    def contains_genre(self, genre):
        genres_list = ['Sitcom', 'Talk', 'Politics', 'Spanish', 'Community', 'Martial arts']
        for g in genres_list:
            if g in genre:
                return True
        return False


    def split_properly(self, line):
              parts = []
              in_quotes = False
              current = []

              for char in line:
                  if char == ',' and not in_quotes:
                      parts.append(''.join(current).strip())
                      current = []
                  elif char == '"':
                      in_quotes = not in_quotes
                  else:
                      current.append(char)

              if current:
                  parts.append(''.join(current).strip())

              return parts

    def mapper(self, _, line):
        if line.startswith("title"):
            return

        fields = self.split_properly(line)

        title = fields[0]
        genres = fields[2]
        air_date = fields[-3]
        air_time =int(fields[-2])


        if 90000 > air_time >= 70000 and \
           self.contains_genre(genres) and \
           self.contains_letter(title):

          yield (title, genres), air_date




    def reducer(self, key, air_date):
        dates_set = set()
        title=key[0]
        genres=key[1]
        genres_count = len(genres.split(','))


        for date in air_date:
            dates_set.add(date)

        count_dates = len(dates_set)
        yield (title, genres), (count_dates, genres_count)

    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer)
        ]

if __name__ == '__main__':
    CompShow.run()
