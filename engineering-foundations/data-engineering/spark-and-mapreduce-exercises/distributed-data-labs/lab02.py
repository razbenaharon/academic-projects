from mrjob.job import MRJob
from mrjob.step import MRStep

class PrimeTimeViewers(MRJob):

    def mapper(self, _, line):
        if line.startswith("mso_code"):
            return

        fields = line.split(',')
        if len(fields) == 6:
            mso_code, device_id, event_date, event_time, station_num, prog_code = fields

            event_time = int(event_time)
            station_num = int(station_num)

            if 200000 <= event_time < 230000 and station_num % 2 == 0:
                yield prog_code, 1


    def reducer(self, prog_code, counts):
        yield None, (sum(counts), prog_code)

    def reducer_find_max(self, _, pair):
            yield max(pair)

    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer),
            MRStep(reducer=self.reducer_find_max)
        ]

if __name__ == '__main__':
    PrimeTimeViewers.run()
