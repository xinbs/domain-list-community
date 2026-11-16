import base64
from pathlib import Path
import tempfile
import unittest

from build_appstore_direct import (
    APP_STORE_DOMAINS,
    CONFIG_FILES,
    GFWLIST_SOURCE,
    GFWLIST_TARGET,
    build_variants,
    exclude_appstore_from_gfwlist,
    exclude_appstore_from_shadowrocket,
)


BASE_CONFIG = '''[General]
ipv6 = false
[Rule]
DOMAIN,apps.apple.com,REJECT
DOMAIN-SUFFIX,apple.com,PROXY
DOMAIN-SUFFIX,mzstatic.com,PROXY
DOMAIN-SUFFIX,google.com,PROXY
FINAL,PROXY
[MITM]
hostname = *.google.cn
'''
BASE_GFWLIST = '''[AutoProxy 0.2.9]
! Expires: 24h
@@||example.cn
||apple.com
||mzstatic.com
||google.com
'''


def first_domain_action(content, host):
    in_rules = False
    for line in content.splitlines():
        if line.startswith('['):
            in_rules = line == '[Rule]'
        if not in_rules:
            continue
        parts = line.split(',')
        if len(parts) != 3:
            continue
        kind, domain, action = parts
        if (kind == 'DOMAIN' and host == domain) or (
            kind == 'DOMAIN-SUFFIX' and
            (host == domain or host.endswith('.' + domain))
        ):
            return action


class AppStoreDirectTests(unittest.TestCase):
    def test_direct_precedes_ad_and_parent_proxy_rules(self):
        content = exclude_appstore_from_shadowrocket(BASE_CONFIG)
        for domain in APP_STORE_DOMAINS:
            for host in (domain, 'test.' + domain):
                with self.subTest(host=host):
                    self.assertEqual(first_domain_action(content, host), 'DIRECT')
        for host in ('apple.com', 'tv.apple.com', 'gsa.apple.com', 'google.com',
                     'apps.apple.com.example', 'notapps.apple.com'):
            with self.subTest(host=host):
                self.assertNotEqual(first_domain_action(content, host), 'DIRECT')

    def test_gfwlist_has_bounded_exceptions_and_preserves_other_filters(self):
        original = base64.b64encode(BASE_GFWLIST.encode())
        content = base64.b64decode(exclude_appstore_from_gfwlist(original),
                                   validate=True).decode()
        self.assertEqual(content.splitlines()[0], '[AutoProxy 0.2.9]')
        for domain in APP_STORE_DOMAINS:
            self.assertIn(f'@@||{domain}^\n', content)
        self.assertTrue(content.endswith(BASE_GFWLIST.split('\n', 1)[1]))
        self.assertNotIn('@@||apple.com', content)

    def test_variants_round_trip_and_base_files_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for source, _ in CONFIG_FILES:
                (output / source).write_text(BASE_CONFIG)
            (output / GFWLIST_SOURCE).write_bytes(
                base64.b64encode(BASE_GFWLIST.encode()))
            originals = {p.name: p.read_bytes() for p in output.iterdir()}
            build_variants(output)
            build_variants(output, verify_only=True)
            for filename, content in originals.items():
                self.assertEqual((output / filename).read_bytes(), content)
            (output / GFWLIST_TARGET).write_bytes(b'broken')
            with self.assertRaises(ValueError):
                build_variants(output, verify_only=True)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            exclude_appstore_from_shadowrocket('[General]\n')
        for content in (b'not base64', base64.b64encode(b'not a GFWList')):
            with self.subTest(content=content), self.assertRaises(ValueError):
                exclude_appstore_from_gfwlist(content)


if __name__ == '__main__':
    unittest.main()
