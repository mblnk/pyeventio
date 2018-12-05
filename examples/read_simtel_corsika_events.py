from eventio import EventIOFile
from eventio.simtel import SimTelMCEvent, SimTelMCShower


with EventIOFile('eventio/resources/gamma_20deg_0deg_run102___cta-prod4-sst-1m_desert-2150m-Paranal-sst-1m.simtel.gz') as f:
    for eventio_object in f:
        if isinstance(eventio_object, SimTelMCShower):
            shower = eventio_object.parse_data_field()
            print('Shower: {shower}, Energy={energy:.3f} TeV'.format(**shower))

        if isinstance(eventio_object, SimTelMCEvent):
            event = eventio_object.parse_data_field()
            event['xcore'] /= 100
            event['ycore'] /= 100

            print('   event: {event}, core_x={xcore:6.2f} m, core_y={ycore:6.2f} m'.format(**event))