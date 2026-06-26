export interface Model {
  id: string;
  provider: 'anthropic' | 'openai';
  is_default?: boolean;
}

export interface ModelConfig {
  models: Model[];
}

export interface SkittleTestRequest {
  model: string;
  environmentId: number;
  dataViewId?: number | null;
  jwt?: string;
  systemPrompt?: string;
  folderId?: string;
  folderValueId?: string;
  userInput: string;
  skill: string;
}

export interface SkittleTestResponse {
  [key: string]: unknown;
}
