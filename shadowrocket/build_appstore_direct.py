#!/usr/bin/env python3
"""Build additional App Store DIRECT variants without changing the base files."""

import argparse
import base64
from pathlib import Path


# Apple lists these domains under "Apps and additional content":
# https://support.apple.com/en-us/101555
# Some music/book content shares these hosts and will also bypass the proxy.
APP_STORE_DOMAINS = ('apps.apple.com', 'itunes.apple.com', 'mzstatic.com')
CONFIG_FILES = (
    ('Shadowrocket_gfwlist.conf', 'Shadowrocket_gfwlist_no_appstore.conf'),
    ('Shadowrocket_gfwlist_ad.conf', 'Shadowrocket_gfwlist_ad_no_appstore.conf'),
)
GFWLIST_SOURCE = 'Shadowrocket_gfwlist.txt'
GFWLIST_TARGET = 'Shadowrocket_gfwlist_no_appstore.txt'


def exclude_appstore_from_shadowrocket(content):
    lines = content.splitlines()
    # Insert before both ad blocking and proxy rules, including apple.com.
    position = lines.index('[Rule]') + 1
    lines[position:position] = [
        '# App Store DIRECT (including shared iTunes / mzstatic content)',
        *(f'DOMAIN-SUFFIX,{domain},DIRECT' for domain in APP_STORE_DOMAINS),
        '',
    ]
    return '\n'.join(lines) + '\n'


def exclude_appstore_from_gfwlist(encoded):
    content = base64.b64decode(encoded, validate=True).decode('utf-8')
    lines = content.splitlines()
    if not lines or lines[0] != '[AutoProxy 0.2.9]':
        raise ValueError('Input is not a standard AutoProxy GFWList')
    # AutoProxy exceptions override proxy filters, including broader apple.com.
    # The ^ boundary prevents matching domains such as apps.apple.com.example.
    lines[1:1] = [
        '! Variant: App Store DIRECT (including shared iTunes / mzstatic content)',
        *(f'@@||{domain}^' for domain in APP_STORE_DOMAINS),
        '',
    ]
    return base64.b64encode(('\n'.join(lines) + '\n').encode('utf-8'))


def build_variants(output_dir, verify_only=False):
    output_dir = Path(output_dir)
    variants = {
        target: exclude_appstore_from_shadowrocket(
            (output_dir / source).read_text(encoding='utf-8')
        ).encode('utf-8')
        for source, target in CONFIG_FILES
    }
    variants[GFWLIST_TARGET] = exclude_appstore_from_gfwlist(
        (output_dir / GFWLIST_SOURCE).read_bytes().strip()
    )
    for filename, expected in variants.items():
        path = output_dir / filename
        if verify_only:
            if path.read_bytes() != expected:
                raise ValueError(f'{filename} differs from the expected DIRECT variant')
            print(f'Verified: {filename}')
        else:
            path.write_bytes(expected)
            print(f'Generated: {filename}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path,
                        default=Path(__file__).parent / 'resultant')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    build_variants(args.output_dir, args.verify_only)


if __name__ == '__main__':
    main()
