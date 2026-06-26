import {Injectable, signal} from '@angular/core';
import {ModelConfig, SkittleTestRequest, SkittleTestResponse} from '../interface/model';

@Injectable({
  providedIn: 'root',
})
export class SkillTesterService {
  private readonly baseUrl = 'http://localhost:8000';

  models = signal<ModelConfig | null>(null);
  modelsLoading = signal(false);
  modelsError = signal<string | null>(null);

  testLoading = signal(false);
  testError = signal<string | null>(null)

  async fetchModels(): Promise<ModelConfig | null> {
    this.modelsLoading.set(true);
    this.modelsError.set(null);

    try {
      const response = await fetch(`${this.baseUrl}/models`);
      if (!response.ok) throw new Error(`Failed to fetch models: ${response.status} ${response.statusText}`);
      const data: ModelConfig = await response.json();
      this.models.set(data);
      return data;
    } catch (err) {
      this.modelsError.set(err instanceof Error ? err.message : 'Failed to fetch models. Please try again later.');
      return null;
    } finally {
      this.modelsLoading.set(false);
    }
  }

  defaultModelId(config: ModelConfig): string {
    return config.models.find(model => model.is_default)?.id ?? '';
  }

  async sendToLLM(payload: SkittleTestRequest): Promise<SkittleTestResponse | null> {
    this.testLoading.set(true);
    this.testError.set(null);

    try {
      const response = await fetch(`${this.baseUrl}/test-skittle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(`Failed to send to LLM: ${response.status} ${response.statusText}`);
      return await response.json();
    } catch (err) {
      this.testError.set(err instanceof Error ? err.message : 'unknown error occurred while sending request to LLM. Please try again later.');
      return null;
    } finally {
      this.testLoading.set(false);
    }
  }
}
