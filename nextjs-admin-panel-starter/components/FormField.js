export default function FormField({ label, ...inputProps }) {
  return (
    <div className="field">
      <label className="label">{label}</label>
      <input className="input" {...inputProps} />
    </div>
  );
}
