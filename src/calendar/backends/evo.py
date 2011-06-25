from calendar.backends.ical import IcalBackend


class EvolutionBackend(IcalBackend):


    def __init__(self, uid, name, type, source):

        IcalBackend.__init__(self, uid, name, type, source)
