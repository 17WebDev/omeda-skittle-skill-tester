export interface Model {
  id: string;
  provider: 'anthropic' | 'openai';
  is_default: boolean;
}

export interface ModelConfig {
  default_provider: 'anthropic' | 'openai';
  models: Model[];
}
