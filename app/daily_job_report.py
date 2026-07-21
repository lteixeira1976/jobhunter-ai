from datetime import datetime
from pathlib import Path
import subprocess
import sys


def main() -> None:
    print("=" * 60)
    print("JOBHUNTER AI — GERANDO ARQUIVO TXT")
    print("=" * 60)

    output_directory = Path("output")
    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_file = output_directory / f"vagas_{timestamp}.txt"

    try:
        result = subprocess.run(
            [sys.executable, "-m", "app.main"],
            input="0\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )

        content = result.stdout.strip()

        if not content:
            content = "Nenhuma informação foi gerada nesta execução."

        if result.returncode != 0 and result.stderr.strip():
            content += "\n\n" + "=" * 60
            content += "\nERRO DURANTE A EXECUÇÃO\n"
            content += "=" * 60 + "\n"
            content += result.stderr.strip()

        output_file.write_text(
            content + "\n",
            encoding="utf-8",
        )

        print()
        print("Arquivo gerado com sucesso:")
        print(output_file.resolve())

    except subprocess.TimeoutExpired as error:
        partial_output = error.stdout or ""

        if isinstance(partial_output, bytes):
            partial_output = partial_output.decode(
                "utf-8",
                errors="replace",
            )

        if partial_output.strip():
            output_file.write_text(
                partial_output.strip() + "\n",
                encoding="utf-8",
            )

            print()
            print("A busca excedeu 10 minutos.")
            print("O resultado parcial foi salvo em:")
            print(output_file.resolve())
        else:
            print()
            print("A busca excedeu 10 minutos sem retornar resultados.")

    except Exception as error:
        print()
        print(f"Erro ao gerar o arquivo: {error}")


if __name__ == "__main__":
    main()