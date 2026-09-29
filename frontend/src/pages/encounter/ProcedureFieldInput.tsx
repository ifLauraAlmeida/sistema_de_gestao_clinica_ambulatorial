import type { ReactElement } from 'react';
import { SelectField } from '../../components/ui/SelectField';
import { TextAreaField } from '../../components/ui/TextAreaField';
import { TextField } from '../../components/ui/TextField';
import type { ExecutionFormField } from '../../types/procedure';
import { fieldLabel } from './procedureForm';

interface ProcedureFieldInputProps {
  field: ExecutionFormField;
  value: string;
  error?: string;
  disabled: boolean;
  onChange: (value: string) => void;
}

const YES_NO = [
  { value: 'true', label: 'Sim' },
  { value: 'false', label: 'Não' },
];

/** Campo do procedimento renderizado conforme o tipo definido no catálogo. */
export function ProcedureFieldInput({
  field,
  value,
  error,
  disabled,
  onChange,
}: ProcedureFieldInputProps): ReactElement {
  const common = { label: fieldLabel(field), value, error, disabled };
  switch (field.field_type) {
    case 'TEXTAREA':
      return <TextAreaField {...common} onChange={(e) => onChange(e.target.value)} />;
    case 'BOOLEAN':
      return (
        <SelectField
          {...common}
          placeholder="—"
          options={YES_NO}
          onChange={(e) => onChange(e.target.value)}
        />
      );
    case 'SELECT':
      return (
        <SelectField
          {...common}
          placeholder="Selecione"
          options={field.options.map((option) => ({ value: option, label: option }))}
          onChange={(e) => onChange(e.target.value)}
        />
      );
    case 'NUMBER':
      return (
        <TextField {...common} inputMode="decimal" onChange={(e) => onChange(e.target.value)} />
      );
    case 'TIME':
      return <TextField {...common} type="time" onChange={(e) => onChange(e.target.value)} />;
    default:
      return <TextField {...common} onChange={(e) => onChange(e.target.value)} />;
  }
}
