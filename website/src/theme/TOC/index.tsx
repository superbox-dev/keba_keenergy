import type {ReactNode} from 'react';
import TOC from '@theme-original/TOC';
import type TOCType from '@theme/TOC';
import type {WrapperProps} from '@docusaurus/types';
import {ListTree} from 'lucide-react';

import ProjectInfo from '@site/src/components/ProjectInfo';

type Props = WrapperProps<typeof TOCType>;

// Right column like the Home Assistant integration pages: project card, then "On this page"
export default function TOCWrapper(props: Props): ReactNode {
    return (
        <div className="ha-aside">
            <ProjectInfo />
            <section className="ha-aside__toc">
                <h2 className="ha-aside__title">
                    <ListTree aria-hidden="true" />{' '}
                    On this page
                </h2>
                <TOC {...props} />
            </section>
        </div>
    );
}
