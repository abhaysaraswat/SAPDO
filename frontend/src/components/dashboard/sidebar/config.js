'use client';

import { 
  GridView as DatasetIcon,
  Description as PromptsIcon,
  Code as PrototypeIcon,
  BarChart as ObserveIcon,
  MenuBook as KnowledgeBaseIcon,
  Assessment as EvalsIcon,
  Task as TasksIcon,
  Key as KeysIcon,
  Chat as ChatIcon
} from '@mui/icons-material';

export const navConfig = [
  {
    items: [
      {
        title: 'Dataset',
        path: '/dashboard/dataset',
        icon: <DatasetIcon fontSize="small" />,
      },
      {
        title: 'Chat',
        path: '/dashboard/chat',
        icon: <ChatIcon fontSize="small" />,
      },
    ],
  },
];
