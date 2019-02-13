from os import path, environ
import pytest
import numpy as np
from eventio import SimTelFile

TEST_FILE_PATH = path.join(
    environ['TEST_FILE_DIR'],
    (
        'gamma_20deg_180deg_run1187___cta-prod3-demo_desert-2150m-Paranal'
        '-demo2sect_cone10.simtel-clean3.gz'
    )
)

TEST_FILE_PATH_NORMAL = path.join(
    environ['TEST_FILE_DIR'],
    (
        'gamma_20deg_180deg_run1187___cta-prod3-demo_desert-2150m-Paranal'
        '-demo2sect_cone10.simtel.gz'
    )
)


def test_adc_sums():
    pyhessio = pytest.importorskip("pyhessio")
    with pyhessio.open_hessio(TEST_FILE_PATH) as hessio_file:
        eventstream = hessio_file.move_to_next_event()
        for EE, HE in zip(SimTelFile(TEST_FILE_PATH), eventstream):
            EE_tel_ids = sorted(EE['telescope_events'].keys())
            HE_tel_ids = sorted(hessio_file.get_teldata_list())
            assert EE_tel_ids == HE_tel_ids

            for tel_id in HE_tel_ids:
                HE_adc_sum = hessio_file.get_adc_sum(tel_id)
                EE_adc_sum = EE['telescope_events'][tel_id]['adc_sums']
                assert np.array_equal(HE_adc_sum, EE_adc_sum)


def test_adc_samples():

    for z, e in zip(
        SimTelFile(TEST_FILE_PATH),
        SimTelFile(TEST_FILE_PATH_NORMAL)
    ):
        for tel_id in e['telescope_events']:
            try:
                zas = z['telescope_events'][tel_id]['adc_samples']
                eas = e['telescope_events'][tel_id]['adc_samples']
                survivors = (zas != 0).all(axis=-1)
                assert survivors.sum() > 0
                assert np.array_equal(zas[survivors], eas[survivors])
            except KeyError as exc:
                print(
                    'event:', e['event_id'],
                    'tel:', tel_id,
                    'KeyError:', exc
                )
