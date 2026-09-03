import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    draft: z.boolean().default(false),
    featured: z.boolean().default(false),
    tags: z.array(z.string()).default([]),
    gear: z.array(z.string()).default([]),
  }),
});

const gear = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/gear' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum(['sim-racing', 'content', 'photography', 'off-road']),
    amazonUrl: z.string().url(),
    featured: z.boolean().default(false),
    usedFor: z.string().optional(),
  }),
});

const partners = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/partners' }),
  schema: z.object({
    name: z.string(),
    offer: z.string(),
    url: z.string().url(),
    code: z.string(),
    featured: z.boolean().default(false),
  }),
});

export const collections = { posts, gear, partners };
