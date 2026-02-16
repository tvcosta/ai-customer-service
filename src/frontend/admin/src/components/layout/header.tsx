interface HeaderProps {
  title: string;
}

export function Header({ title }: HeaderProps) {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="flex h-16 items-center px-8">
        <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
      </div>
    </header>
  );
}
