import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const repository = 'https://github.com/superbox-dev/keba_keenergy';

const config: Config = {
    title: 'KEBA KeEnergy',
    tagline: 'A Home Assistant integration for heat pumps with a KEBA KeEnergy control unit.',
    favicon: 'img/logo.svg',

    future: {
        v4: true,
    },

    url: 'https://superbox-dev.github.io',
    baseUrl: '/keba_keenergy/',
    trailingSlash: false,

    organizationName: 'superbox-dev',
    projectName: 'keba_keenergy',

    onBrokenLinks: 'throw',
    onBrokenAnchors: 'throw',

    markdown: {
        // The pages are copied from website/content and the repository Markdown files, so parse them as CommonMark
        format: 'detect',
        hooks: {
            onBrokenMarkdownLinks: 'throw',
        },
    },

    i18n: {
        defaultLocale: 'en',
        locales: ['en'],
    },

    presets: [
        [
            'classic',
            {
                docs: {
                    routeBasePath: '/',
                    sidebarPath: './sidebars.ts',
                },
                blog: false,
                sitemap: {
                    // The search page has no content of its own
                    ignorePatterns: ['/keba_keenergy/search'],
                },
                theme: {
                    customCss: './src/css/custom.css',
                },
            } satisfies Preset.Options,
        ],
    ],

    themes: [
        [
            '@easyops-cn/docusaurus-search-local',
            {
                hashed: true,
                docsRouteBasePath: '/',
                indexBlog: false,
                highlightSearchTermsOnTargetPage: true,
                // "/" is handled in src/searchShortcut.ts, independent of the keyboard layout
                searchBarShortcut: false,
                searchBarShortcutHint: false,
            },
        ],
    ],

    clientModules: ['./src/searchShortcut.ts'],

    themeConfig: {
        image: 'img/social-card.png',
        colorMode: {
            defaultMode: 'light',
            disableSwitch: true,
            respectPrefersColorScheme: false,
        },
        docs: {
            sidebar: {
                hideable: true,
            },
        },
        navbar: {
            title: 'KEBA KeEnergy',
            logo: {
                alt: 'superbox logo',
                src: 'img/logo.svg',
            },
            items: [
                {type: 'doc', docId: 'index', label: 'Documentation', position: 'right'},
                {type: 'doc', docId: 'changelog', label: 'Changelog', position: 'right'},
                {href: repository, label: 'GitHub', position: 'right'},
            ],
        },
        footer: {
            links: [
                {
                    title: 'Documentation',
                    items: [
                        {label: 'Integration', to: '/'},
                        {label: 'Changelog', to: '/changelog'},
                        {label: 'Contributing', to: '/contributing'},
                    ],
                },
                {
                    title: 'Community',
                    items: [
                        {label: 'Issues', href: `${repository}/issues`},
                        {label: 'Discord', href: 'https://discord.com/users/superbox_dev'},
                        {label: 'Donation', to: '/donation'},
                    ],
                },
                {
                    title: 'More',
                    items: [
                        {label: 'GitHub', href: repository},
                        {label: 'HACS', href: 'https://hacs.xyz'},
                        {label: 'API library', href: 'https://superbox-dev.github.io/keba_keenergy_api/'},
                    ],
                },
            ],
            copyright: `Copyright © ${new Date().getFullYear()} Michael Hacker. Licensed under Apache-2.0.`,
        },
        prism: {
            theme: prismThemes.github,
            darkTheme: prismThemes.oneDark,
            additionalLanguages: ['bash', 'json', 'yaml'],
        },
    } satisfies Preset.ThemeConfig,
};

export default config;
