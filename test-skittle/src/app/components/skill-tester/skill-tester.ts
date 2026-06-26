import {Component, computed, signal} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {ModelConfig} from '../../interface/model';
import {requiredNumber, requiredString} from '../../utils/field-validation.utils';

@Component({
  selector: 'app-skill-tester',
  imports: [FormsModule],
  templateUrl: './skill-tester.html',
  styleUrl: './skill-tester.css',
})
export class SkillTester {
  readonly modelOptions: ModelConfig = {
    default_provider: 'openai',
    models: [
      { id: 'claude-opus-4-8',   provider: 'anthropic', is_default: true  },
      { id: 'claude-opus-4-7',   provider: 'anthropic', is_default: false },
      { id: 'claude-sonnet-4-6', provider: 'anthropic', is_default: false },
      { id: 'claude-haiku-4-5',  provider: 'anthropic', is_default: false },
      { id: 'gpt-4o',            provider: 'openai',    is_default: false },
      { id: 'gpt-4o-mini',       provider: 'openai',    is_default: false },
      { id: 'gpt-4-turbo',       provider: 'openai',    is_default: false },
      { id: 'gpt-3.5-turbo',     provider: 'openai',    is_default: false },
    ]
  };

  readonly defaultModel = this.modelOptions.models.find(model => model.is_default)?.id ?? '';

  model = signal(this.defaultModel);
  environmentId = signal<number | null>(null);
  dataViewId = signal<number | null>(null);
  jwt = signal('');
  systemPrompt = signal('');
  folderId = signal('');
  folderValueId = signal('');
  userInput = signal('');
  skill = signal('');
  payloadOutput = signal('');

  environmentIdTouched = signal(false);
  modelTouched = signal(false)
  skillTouched = signal(false);

  environmentIdError = requiredNumber(this.environmentId, this.environmentIdTouched, 'Environment ID');
  modelError = requiredString(this.model, this.modelTouched, 'Model');
  skillError = requiredString(this.skill, this.skillTouched, 'Skill');

  isValid = computed(() =>
    this.environmentId() !== null &&
    this.model().trim() !== '' &&
    this.skill().trim() !== ''
  );

  sentToLLM(): void {
    this.environmentIdTouched.set(true);
    this.modelTouched.set(true);
    this.skillTouched.set(true);

    if (!this.isValid()) return

    const payload = {
      model: this.model(),
      environmentId: this.environmentId(),
      dataViewId: this.dataViewId(),
      jwt: this.jwt(),
      systemPrompt: this.systemPrompt(),
      folderId: this.folderId(),
      folderValueId: this.folderValueId(),
      userInput: this.userInput(),
      skill: this.skill()
    };
    this.payloadOutput.set(JSON.stringify(payload, null, 2));
    console.log(`Sent to LLM: ${this.payloadOutput()}`);
  }

  sentToFrontend(): void {
    console.log(`Sent to Frontend: ${this.payloadOutput()}`);
  }
}
