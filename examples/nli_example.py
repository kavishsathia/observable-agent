from sworn import Contract, Commitment, nli_verifier


contract = Contract()

contract.add_commitment(Commitment(
    name="file_naming_policy",
    terms="Files must be named with .txt extension",
    verifier=nli_verifier,
    semantic_sampling_rate=0.0
))

contract.add_commitment(Commitment(
    name="confirmation_required",
    terms="Destructive actions require user confirmation",
    verifier=nli_verifier,
    semantic_sampling_rate=0.0
))


@contract.actuator
def write_file(filename: str, content: str) -> dict:
    print(f"Writing to {filename}")
    return {"status": "success", "filename": filename}


@contract.actuator
def delete_file(filename: str, confirmed: bool = False) -> dict:
    print(f"Deleting {filename} (confirmed: {confirmed})")
    return {"status": "deleted", "filename": filename}


def main():
    with contract.execution() as execution:
        write_file("report.txt", "Q3 summary")
        write_file("data.csv", "1,2,3")
        delete_file("old_data.txt", confirmed=True)

        results = execution.verify()

        print("\nVerification Results:")
        for result in results:
            print(f"\n{result.commitment_name}: {result.status.value}")
            print(f"  Expected: {result.expected}")
            print(f"  Actual: {result.actual}")
            if result.context:
                print(f"  Confidence: {result.context.get('confidence', 'N/A')}")


if __name__ == "__main__":
    main()
