import fs from 'fs/promises';
import path from 'path';

export async function loadTranslation(locale: string, namespace: string) {
  const filePath = path.join(process.cwd(), 'public', 'locales', locale, `${namespace}.json`);
  try {
    const fileContents = await fs.readFile(filePath, 'utf8');
    return JSON.parse(fileContents);
  } catch (error) {
    console.error(`Failed to load translation for ${locale}/${namespace}:`, error);
    return {};
  }
}
