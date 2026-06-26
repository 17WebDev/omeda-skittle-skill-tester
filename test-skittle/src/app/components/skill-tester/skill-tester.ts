import {Component, computed, inject, OnInit, signal} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {ModelConfig, SkittleTestRequest} from '../../interface/model';
import {requiredNumber, requiredString} from '../../utils/field-validation.utils';
import {SkillTesterService} from '../../services/skill-tester.service';

@Component({
  selector: 'app-skill-tester',
  imports: [FormsModule],
  templateUrl: './skill-tester.html',
  styleUrl: './skill-tester.css',
})
export class SkillTester implements OnInit{
  protected readonly skillTesterService = inject(SkillTesterService);

  model = signal('');
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

  async ngOnInit(): Promise<void> {
    const config = await this.skillTesterService.fetchModels();
    if (config) {
      this.model.set(this.skillTesterService.defaultModelId(config));
    }
  }

  isValid = computed(() =>
    this.environmentId() !== null &&
    this.model().trim() !== '' &&
    this.skill().trim() !== ''
  );

  async sentToLLM(): Promise<void> {
    this.environmentIdTouched.set(true);
    this.modelTouched.set(true);
    this.skillTouched.set(true);

    if (!this.isValid()) return

    const payload: SkittleTestRequest = {
      model: this.model(),
      environmentId: this.environmentId()!,
      dataViewId: this.dataViewId(),
      jwt: this.jwt(),
      systemPrompt: this.systemPrompt(),
      folderId: this.folderId(),
      folderValueId: this.folderValueId(),
      userInput: this.userInput(),
      skill: this.skill()
    };

    const result = await this.skillTesterService.sendToLLM(payload);
    if (result) {
      this.payloadOutput.set(JSON.stringify(result, null, 2));
    }

  }

  sentToFrontend(): void {
    console.log(`Sent to Frontend: ${this.payloadOutput()}`);
  }
}
