export type NavLink = [href: string, label: string];

export type NavGroup = {
  label: string;
  description: string;
  links: NavLink[];
};

export const navGroups: NavGroup[] = [
  {
    label: 'Investigate',
    description: 'Read a regional trend, compare places, inspect satellite context, and test a trained model.',
    links: [
      ['/mission-control', 'Mission control'],
      ['/discover', 'Guided discovery'],
      ['/satellite', 'Satellite explorer'],
      ['/compare', 'Compare regions'],
      ['/ml', 'ML Lab']
    ]
  },
  {
    label: 'Earth systems',
    description: 'See the same record on a globe, in paired signals, in a contradiction audit, and under a conditional scenario.',
    links: [
      ['/earth', '3D Earth'],
      ['/mirage', 'Green Mirage'],
      ['/atlas', 'Contradiction Atlas'],
      ['/twin', 'Digital Twin']
    ]
  },
  {
    label: 'Reference',
    description: 'Check the methods, reports, source catalog, answers, and the synthetic teaching example.',
    links: [
      ['/methods', 'Science guide'],
      ['/reports', 'Research reports'],
      ['/catalog', 'Data catalog'],
      ['/faq', 'FAQ'],
      ['/example', 'Learning lab']
    ]
  }
];
