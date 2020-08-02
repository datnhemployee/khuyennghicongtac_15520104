import copy


class Step():
    def __init__(self, name: str, inputs: dict, outputs: dict, output_file: str, default_icon=""):
        self.name = name
        self.inputs = copy.deepcopy(inputs)
        self.outputs = copy.deepcopy(outputs)
        self.output_file = output_file
        self.excuting = False
        self.default_icon = default_icon

    def to_str_output(self) -> str:
        result = ""
        for key in self.outputs.keys():
            result += key+" - "+self.outputs[key]

        return result

    # def is_finished(self) -> bool:
    #     from utils.file import existing_file
    #     is_fisnished = existing_file(self.output_file)
    #     return is_fisnished
