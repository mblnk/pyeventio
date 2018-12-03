"""
    RunHeader[2000]
    MCRunHeader[2001]
    CORSIKAInputCard[1212]

        # 1x per telescope (n_telescopes is in RunHeader)
        # I call this TelescopeDescription
    {
        SimTelCamSettings[2002]
        SimTelCamOrgan[2003]
        SimTelPixelset[2004]
        SimTelPixelDisable[2005]
        SimTelCamsoftset[2006]
        SimTelTrackSet[2008]
        SimTelPointingCor[2007]
    }

    {
        MCShower[2020](shower=3)
        {
            MCEvent[2021](event=301)
            CORSIKATelescopeData[1204](event=301)
                # IACTPhotoElectrons inside

            { 1x per telescope and I don't know why they come here
            TelMoni[2022](telescope_id=1, what=0x7f)
            LasCal[2023](telescope_id=1)
            }
            MCPeSum[2026](id=301)
            Event[2010]
            {
                CentEvent[2009](id=301)
                TelEvent[2229](telescope_id=29, id=301)
                {
                    TelEvtHead[2011](telescope_id=29)
                    TelADCSamp[2013](telescope_id=29,
                    PixelTiming[2016](telescope_id=29)
                    TelImage[2014](telescope_id=29,
                    PixelList[2027](telescope_id=29
                }
                TelEvent[2237](telescope_id=37, id=301)
                TrackEvent[2113](telescope_id=13
                TrackEvent[2117](telescope_id=17
                TrackEvent[2123](telescope_id=23
                TrackEvent[2129](telescope_id=29
                TrackEvent[2131](telescope_id=31
                ...
                TrackEvent[2163](telescope_id=63
                Shower[2015]
            }
        }


    }


"""
from eventio.base import EventIOFile
from eventio.iact.objects import CORSIKAInputCard, CORSIKATelescopeData
from eventio.simtel.objects import (
    History,
    TelescopeObject,
    SimTelRunHeader,
    SimTelMCRunHeader,
    SimTelCamSettings,
    SimTelCamOrgan,
    SimTelPixelset,
    SimTelPixelDisable,
    SimTelCamsoftset,
    SimTelPointingCor,
    SimTelTrackSet,
    SimTelCentEvent,
    SimTelTrackEvent,
    SimTelTelEvent,
    SimTelEvent,
    SimTelTelEvtHead,
    SimTelTelADCSum,
    SimTelTelADCSamp,
    SimTelTelImage,
    SimTelShower,
    SimTelPixelTiming,
    SimTelPixelCalib,
    SimTelMCShower,
    SimTelMCEvent,
    SimTelTelMoni,
    SimTelLasCal,
    SimTelRunStat,
    SimTelMCRunStat,
    SimTelMCPeSum,
    SimTelPixelList,
    SimTelCalibEvent,
)


class SimTelFile:
    def __init__(self, path):
        self.path = path
        self.file_ = EventIOFileWithNextAssert(path)

        self.history = []
        while True:
            try:
                self.history.append(self.file_.next_assert(History))
            except WrongType:
                break

        self.header = self.file_.next_assert(SimTelRunHeader)
        self.mc_header = []
        while True:
            try:
                self.mc_header.append(self.file_.next_assert(SimTelMCRunHeader))
            except WrongType:
                break

        self.corsika_input = []
        while True:
            try:
                self.corsika_input.append(self.file_.next_assert(CORSIKAInputCard))
            except WrongType:
                break


        self.n_telescopes = self.header.parse_data_field()['n_telescopes']
        self.telescope_descriptions = [
            telescope_description_from(self.file_)
            for _ in range(self.n_telescopes)
        ]

        self.shower = None

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            shower, event = self.fetch_next_event()
            if 'event' in event:
                return shower, event

    def fetch_next_event(self):
        try:
            event = self.next_mc_event()
            return self.shower, event
        except WrongType:
            try:
                self.shower = self.file_.next_assert(SimTelMCShower)
                event = self.next_mc_event()
                return self.shower, event
            except WrongType:
                raise StopIteration

    def next_mc_event(self):
        result = {}
        result['mc_event'] = self.file_.next_assert(SimTelMCEvent)
        try:
            result['corsika_tel_data'] = self.file_.next_assert(CORSIKATelescopeData)
        except WrongType:
            pass

        try:
            result['moni_lascal'] = [
                (
                    self.file_.next_assert(SimTelTelMoni),
                    self.file_.next_assert(SimTelLasCal),
                )
                for _ in range(self.n_telescopes)
            ]
        except WrongType:
            pass

        try:
            result['pe_sum'] = self.file_.next_assert(SimTelMCPeSum)
            result['event'] = self.file_.next_assert(SimTelEvent)
        except WrongType:
            pass

        return result


class WrongType(Exception):
    pass


class WithNextAssert:
    '''MixIn for EventIoFile adding `next_assert`'''

    def next_assert(self, object_):
        '''return next object from file, only
        if it is of type `object_`
        else raise WrongType

        Make sure the object is not lost, but another call to next_assert
        will see the exact same object
        '''
        if not hasattr(self, '_last_obj'):

            self._last_obj = None

        if self._last_obj is None:
            self._last_obj = next(self)

        o = self._last_obj

        if not isinstance(o, object_):
            raise WrongType(f"is:{o}, not:{object_}")

        self._last_obj = None
        return o


class EventIOFileWithNextAssert(EventIOFile, WithNextAssert):
    pass


def telescope_description_from(file_):
    return [
        file_.next_assert(SimTelCamSettings),
        file_.next_assert(SimTelCamOrgan),
        file_.next_assert(SimTelPixelset),
        file_.next_assert(SimTelPixelDisable),
        file_.next_assert(SimTelCamsoftset),
        file_.next_assert(SimTelTrackSet),
        file_.next_assert(SimTelPointingCor),
    ]

