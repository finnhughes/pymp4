#!/usr/bin/env python
"""
   Copyright 2016 beardypig

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import logging
import unittest
import io

from construct import Container
from pymp4.parser import Box, SampleEntryBox, TrackNameBox, NameBox, TrackTitleBox

log = logging.getLogger(__name__)


class BoxTests(unittest.TestCase):
    def test_ftyp_parse(self):
        self.assertEqual(
            Box.parse(b'\x00\x00\x00\x18ftypiso5\x00\x00\x00\x01iso5avc1'),
            Container(offset=0)
            (type=b"ftyp")
            (major_brand=b"iso5")
            (minor_version=1)
            (compatible_brands=[b"iso5", b"avc1"])
            (end=24)
        )

    def test_ftyp_build(self):
        self.assertEqual(
            Box.build(dict(
                type=b"ftyp",
                major_brand=b"iso5",
                minor_version=1,
                compatible_brands=[b"iso5", b"avc1"])),
            b'\x00\x00\x00\x18ftypiso5\x00\x00\x00\x01iso5avc1')

    def test_mdhd_parse(self):
        self.assertEqual(
            Box.parse(
                b'\x00\x00\x00\x20mdhd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0fB@\x00\x00\x00\x00U\xc4\x00\x00'),
            Container(offset=0)
            (type=b"mdhd")(version=0)(flags=0)
            (creation_time=0)
            (modification_time=0)
            (timescale=1000000)
            (duration=0)
            (language="und")
            (end=32)
        )

    def test_mdhd_build(self):
        mdhd_data = Box.build(dict(
            type=b"mdhd",
            creation_time=0,
            modification_time=0,
            timescale=1000000,
            duration=0,
            language=u"und"))
        self.assertEqual(len(mdhd_data), 32)
        self.assertEqual(mdhd_data,
                         b'\x00\x00\x00\x20mdhd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0fB@\x00\x00\x00\x00U\xc4\x00\x00')

        mdhd_data64 = Box.build(dict(
            type=b"mdhd",
            version=1,
            creation_time=0,
            modification_time=0,
            timescale=1000000,
            duration=0,
            language=u"und"))
        self.assertEqual(len(mdhd_data64), 44)
        self.assertEqual(mdhd_data64,
                         b'\x00\x00\x00,mdhd\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0fB@\x00\x00\x00\x00\x00\x00\x00\x00U\xc4\x00\x00')

    def test_moov_build(self):
        moov = \
            Container(type=b"moov")(children=[  # 96 bytes
                Container(type=b"mvex")(children=[  # 88 bytes
                    Container(type=b"mehd")(version=0)(flags=0)(fragment_duration=0),  # 16 bytes
                    Container(type=b"trex")(track_ID=1),  # 32 bytes
                    Container(type=b"trex")(track_ID=2),  # 32 bytes
                ])
            ])

        moov_data = Box.build(moov)

        self.assertEqual(len(moov_data), 96)
        self.assertEqual(
            moov_data,
            b'\x00\x00\x00\x60moov'
            b'\x00\x00\x00\x58mvex'
            b'\x00\x00\x00\x10mehd\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x20trex\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x20trex\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        )

    def test_smhd_parse(self):
        in_bytes = b'\x00\x00\x00\x10smhd\x00\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual(
            Box.parse(in_bytes + b'padding'),
            Container(offset=0)
            (type=b"smhd")(version=0)(flags=0)
            (balance=0)(reserved=0)(end=len(in_bytes))
        )

    def test_smhd_build(self):
        smhd_data = Box.build(dict(
            type=b"smhd",
            balance=0))
        self.assertEqual(len(smhd_data), 16),
        self.assertEqual(smhd_data, b'\x00\x00\x00\x10smhd\x00\x00\x00\x00\x00\x00\x00\x00')

    def test_stsd_parse(self):
        tx3g_data = b'\x00\x00\x00\x00\x01\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x12\xFF\xFF\xFF\xFF\x00\x00\x00\x12ftab\x00\x01\x00\x01\x05Serif'
        in_bytes = b'\x00\x00\x00\x50stsd\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x40tx3g\x00\x00\x00\x00\x00\x00\x00\x01' + tx3g_data
        self.assertEqual(
            Box.parse(in_bytes + b'padding'),
            Container(offset=0)
            (type=b"stsd")(version=0)(flags=0)
            (entries=[Container(format=b'tx3g')(data_reference_index=1)(data=tx3g_data)])
            (end=len(in_bytes))
        )

    def test_avc1_parse(self):
        compressor = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        sps = b'\x67\x4d\x40\x29\xe8\x80\x28\x02\xdd\xff\x80\x0d\x80\x0a\x08\x00\x00\x1f\x48\x00\x05\xdc\x00\x78\xc1\x88\x90'
        pps = b'\x68\xeb\x8c\xb2'
        input_bytes = (
            b'\x00\x00\x00\x98avc1\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x02\xd0\x00\x48\x00\x00\x00\x48\x00\x00\x00\x00\x00\x00\x00\x01' + compressor + b'\x00\x18\xff\xff'
            b'\x00\x00\x00\x32avcC\x01\x4d\x40\x29\xff\xe1\x00\x1b' + sps + b'\x01\x00\x04' + pps +
            b'\x00\x00\x00\x10pasp\x00\x00\x00\x1b\x00\x00\x00\x14'
        )
        expected = (
            Container(format=b'avc1')(data_reference_index=1)(version=0)(revision=0)(vendor=b'\x00\x00\x00\x00')
            (temporal_quality=0)(spatial_quality=0)(width=1280)(height=720)(horizontal_resolution=72)
            (vertical_resolution=72)(data_size=0)(frame_count=1)(compressor_name=compressor)(depth=24)(color_table_id=-1)
            (extensions=[
                Container(type=b'avcC')(version=1)(profile=77)(compatibility=64)(level=41)(nal_unit_length_field=3)(sps=[sps])(pps=[pps]),
                Container(type=b'pasp')(h_spacing=27)(v_spacing=20)
            ])
        )
        input_stream = io.BytesIO(input_bytes + b'padding')
        self.assertEqual(SampleEntryBox.parse_stream(input_stream), expected)
        self.assertEqual(input_stream.tell(), len(input_bytes))

    def test_udta_parse(self):
        ilst = b'\x00\x00\x00\x25\xA9\x74\x6F\x6F\x00\x00\x00\x1D\x64\x61\x74\x61\x00\x00\x00\x01\x00\x00\x00\x00\x4C\x61\x76\x66\x35\x37\x2E\x32\x35\x2E\x31\x30\x30'
        input_bytes = (
            b'\x00\x00\x00\x62udta'
            b'\x00\x00\x00\x5ameta\x00\x00\x00\x00'
            b'\x00\x00\x00\x21hdlr\x00\x00\x00\x00\x00\x00\x00\x00mdir\x61\x70\x70\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x2Dilst' + ilst
        )
        self.assertEqual(
            Box.parse(input_bytes),
            Container(offset=0)(type=b'udta')
            (children=[
                Container(offset=8)(type=b'meta')(version=0)(flags=0)(children=[
                    Container(offset=20)(type=b'hdlr')(version=0)(flags=0)(handler_type=b'mdir')(name=u'')(end=53),
                    Container(offset=53)(type=b'ilst')(data=ilst)(end=len(input_bytes))
                ])(end=len(input_bytes))
            ])(end=len(input_bytes))
        )

    def test_udta_terminator_parse(self):
        ilst = b'\x00\x00\x00\x25\xA9\x74\x6F\x6F\x00\x00\x00\x1D\x64\x61\x74\x61\x00\x00\x00\x01\x00\x00\x00\x00\x4C\x61\x76\x66\x35\x37\x2E\x32\x35\x2E\x31\x30\x30'
        input_bytes = (
                b'\x00\x00\x00\x66udta'
                b'\x00\x00\x00\x5ameta\x00\x00\x00\x00'
                b'\x00\x00\x00\x21hdlr\x00\x00\x00\x00\x00\x00\x00\x00mdir\x61\x70\x70\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x2Dilst' + ilst +
                b'\x00\x00\x00\x00'

        )
        self.assertEqual(
            Box.parse(input_bytes),
            Container(offset=0)(type=b'udta')
                (children=[
                Container(offset=8)(type=b'meta')(version=0)(flags=0)(children=[
                    Container(offset=20)(type=b'hdlr')(version=0)(flags=0)(handler_type=b'mdir')(name=u'')(end=53),
                    Container(offset=53)(type=b'ilst')(data=ilst)(end=len(input_bytes)-4)
                ])(end=len(input_bytes)-4)
            ])(end=len(input_bytes))
        )

    def test_tnam_parse(self):
        input_bytes = b'tnam\x00\x00\x00\x00\x15\xC7TT\x00'
        self.assertEqual(
            TrackNameBox.parse(input_bytes),
            Container(type=b'tnam')(version=0)(flags=0)
            (language=u'eng')(value=u'TT\x00')
        )

    def test_name_parse(self):
        input_bytes = b'nameLatino\x00'
        self.assertEqual(
            NameBox.parse(input_bytes),
            Container(type=b'name')(value=u'Latino\x00')
        )
