import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {
  mdiAccountGroup,
  mdiBug,
  mdiLan,
  mdiGithub,
  mdiHistory,
  mdiHomeAssistant,
  mdiLightbulbQuestion,
  mdiShape,
} from '@mdi/js';

import hacs from '@site/../hacs.json';
import manifest from '@site/../custom_components/keba_keenergy/manifest.json';

import styles from './styles.module.css';

const repository = 'https://github.com/superbox-dev/keba_keenergy';
// Explanation of the IoT classes in the Home Assistant blog
const iotClasses = 'https://www.home-assistant.io/blog/2016/02/12/classifying-the-internet-of-things/';
const categories = ['Climate', 'Energy', 'Sensor', 'Water heater'];

function Icon({path}: {path: string}): ReactNode {
  return (
    <svg className={styles.icon} viewBox="0 0 24 24" aria-hidden="true">
      <path d={path} />
    </svg>
  );
}

// "local_polling" -> "Local Polling", the anchor in the blog is "#local-polling"
function iotClass(): {label: string; anchor: string} {
  const words = manifest.iot_class.split('_');
  return {
    label: words.map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    anchor: words.join('-'),
  };
}

// Integration card above the table of contents, styled after the Home Assistant integration sidebar
export default function ProjectInfo(): ReactNode {
  const {label, anchor} = iotClass();

  return (
    <div className={styles.projectInfo}>
      <section className={styles.module}>
        <div className={styles.logo}>
          <span className={styles.name}>{manifest.name}</span>
          <Link href={`${repository}/releases`}>
            <img
              src="https://img.shields.io/github/v/release/superbox-dev/keba_keenergy?label=Release"
              alt="Latest release on GitHub"
              height={20}
            />
          </Link>
        </div>
        <p className={styles.section}>
          A custom integration, installed with <Link href="https://hacs.xyz">HACS</Link>. It requires Home Assistant{' '}
          {hacs.homeassistant} or newer.
        </p>
        <p className={styles.section}>
          A community project, not affiliated with or endorsed by KEBA. KEBA and KeEnergy are trademarks of their
          owner.
        </p>
        <p className={styles.section}>
          <Icon path={mdiLan} /> Its IoT class is <Link href={`${iotClasses}#${anchor}`}>{label}</Link>.
        </p>
        <p className={styles.section}>
          <Link href={repository}>
            <Icon path={mdiGithub} /> View source on GitHub
          </Link>
          <br />
          <Link href={`${repository}/issues?q=is%3Aissue+is%3Aopen+label%3Abug`}>
            <Icon path={mdiBug} /> View known issues
          </Link>
          <br />
          <Link href={`${repository}/issues/new/choose`}>
            <Icon path={mdiLightbulbQuestion} /> Request a feature
          </Link>
          <br />
          <Link href={`https://my.home-assistant.io/redirect/config_flow_start/?domain=${manifest.domain}`}>
            <Icon path={mdiHomeAssistant} /> Add to Home Assistant
          </Link>
          <br />
          <Link to="/changelog">
            <Icon path={mdiHistory} /> Changelog
          </Link>
        </p>
      </section>
      <section className={styles.module}>
        <h2 className={styles.title}>
          <Icon path={mdiShape} /> Categories
        </h2>
        <ul className={styles.list}>
          {categories.map((category) => (
            <li key={category}>{category}</li>
          ))}
        </ul>
      </section>
      <section className={styles.module}>
        <h2 className={styles.title}>
          <Icon path={mdiAccountGroup} /> Code owners
        </h2>
        {manifest.codeowners.map((codeowner) => {
          const user = codeowner.replace(/^@/, '');
          return (
            <Link key={user} className={styles.owner} href={`https://github.com/${user}`}>
              <img src={`https://avatars.githubusercontent.com/${user}?size=96`} alt="" width={32} height={32} />
              {codeowner}
            </Link>
          );
        })}
      </section>
    </div>
  );
}
