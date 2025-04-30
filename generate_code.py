from collections import defaultdict
from javaFileWriter import javaFileWriter
import json
from utils import *
from java_test import analysis_java_files

java_root = "./test"

prompt = "Give me the dependency relationship of all following classes. For example, the class \"BookRepository\" " \
         "depends on the class \"Book\", and the class \"Book\" doesn't depend on any other classes.\nClass data:" + \
         get_definition_results()


# dependency_result = generation(prompt, all_dependency_relationships)


def determine_level(data):
    dependencies = defaultdict(list)
    dependents = defaultdict(list)

    for item in data:
        class_name = item["class_name"]
        dependencies[class_name] = [dep["dependency_class_name"] for dep in item["list_of_dependencies"]]
        for dep in dependencies[class_name]:
            dependents[dep].append(class_name)

    levels = {}

    def determine_level_recursive(class_name):
        if class_name in levels:
            return levels[class_name]
        if not dependencies[class_name]:
            levels[class_name] = 1
            return 1
        level = 1 + max(determine_level_recursive(dep) for dep in dependencies[class_name])
        levels[class_name] = level
        return level

    classes = list(dependencies.keys())
    for class_name in classes:
        determine_level_recursive(class_name)
    return dependencies, list(levels.items())


# dependency_dict, dependency_levels = determine_level(dependency_result.dict()['list_of_dependency_relationships'])
# max_level = max(level for _, level in dependency_levels)

code_storage = {}
rag = get_rag()
java_lib = analysis_java_files('./spring-lib')
rag.batch_add_data(java_lib.items())
outputs = rag.query('decode json files', 10)
print(outputs)
# for current_level in range(1, max_level + 1):
#     for class_name, level in dependency_levels:
#         if current_level != level: continue
#         print("generating class: ", class_name, ", dependency: ", dependency_dict[class_name], ", level: ",
#               current_level, sep="")
#         prompt = class_generation_prompt(class_name, dependency_dict[class_name], code_storage)
#         code_storage[class_name] = generation(prompt, code_generation)
#
#         class_definitions = json.loads(get_definition_results())
#         rag.add_data()
#         # import dependencies
#         for i in dependency_dict[class_name]:
#             for j in class_definitions:
#                 if j['class_name'] == i:
#                     current_class_type = j['class_type']
#             code_storage[class_name].imports += "\nimport generation.code.test." + current_class_type + "." + i + ";"
#         current_class_type = ""
#         for i in class_definitions:
#             if i['class_name'] == class_name:
#                 current_class_type = i['class_type']
#         if current_class_type == classType.model or current_class_type == "model":
#             # solve getter/setter
#             code_storage[class_name].imports += "\nimport lombok.Data;"
#             code_storage[class_name].contents = "\n@Data\n" + code_storage[class_name].contents.lstrip()
#
#         javaFileWriter(java_root, class_name, code_storage[class_name], current_class_type)
# ['T read(JsonParser parser, Class<T> type) throws IOException {\r\n\t\tif (ObjectNode.class.isAssignableFrom(type))
# {\r\n\t\t\tObjectNode node = this.objectMapper.readTree(parser);
# \r\n\t\t\tif (node == null || node.isMissingNode() || node.isEmpty()) {
# \r\n\t\t\t\treturn null;\r\n\t\t\t}\r\n\t\t\treturn (T) node;
# \r\n\t\t}\r\n\t\treturn this.objectMapper.readValue(parser, type);
# \r\n\t}', 'void extractingJsonPathStringValueForEmptyString() {
# \r\n\t\tassertThat(forJson(TYPES)).extractingJsonPathStringValue("@.emptyString").isEmpty();
# \r\n\t}', 'void extractingJsonPathStringValueForMissing() {
# \r\n\t\tassertThat(forJson(TYPES)).extractingJsonPathStringValue("@.bogus").isNull();
# \r\n\t}', 'void get(InputStream content, Class<T> type, Consumer<T> consumer) throws IOException {
# \r\n\t\tJsonFactory jsonFactory = this.objectMapper.getFactory();
# \r\n\t\ttry (JsonParser parser = jsonFactory.createParser(content)) {
# \r\n\t\t\twhile (!parser.isClosed()) {
# \r\n\t\t\t\tJsonToken token = parser.nextToken();
# \r\n\t\t\t\tif (token != null && token != JsonToken.END_OBJECT) {
# \r\n\t\t\t\t\tT node = read(parser, type);
# \r\n\t\t\t\t\tif (node != null) {
# \r\n\t\t\t\t\t\tconsumer.accept(node);
# \r\n\t\t\t\t\t}\r\n\t\t\t\t}\r\n\t\t\t}
# \r\n\t\t}\r\n\t}', 'void extractingJsonPathValueForMissing() {
# \r\n\t\tassertThat(forJson(TYPES)).extractingJsonPathValue("@.bogus").isNull();
# \r\n\t}', 'void extractingJsonPathStringValueForWrongType() {
# \r\n\t\tString expression = "$.num";
# \r\n\t\tassertThatExceptionOfType(AssertionError.class)
# \r\n\t\t\t.isThrownBy(() -> assertThat(forJson(TYPES)).extractingJsonPathStringValue(expression))
# \r\n\t\t\t.withMessageContaining("Expected a string at JSON path \\"" + expression + "\\" but found: 5");
# \r\n\t}', 'void extractingJsonPathArrayValueForMissing() {
# \r\n\t\tassertThat(forJson(TYPES)).extractingJsonPathArrayValue("@.bogus").isNull();
# \r\n\t}', 'void extractingJsonPathStringValue() {
# \r\n\t\tassertThat(forJson(TYPES)).extractingJsonPathStringValue("@.str").isEqualTo("foo");
# \r\n\t}', 'AbstractCharSequenceAssert<?, String> extractingJsonPathStringValue(CharSequence expression,
# \r\n\t\t\tObject... args) {\r\n\t\treturn Assertions.assertThat(extractingJsonPathValue(expression, args, String.class, "a string"));
# \r\n\t}', 'void extractingJsonPathValue() {
# \r\n\t\tassertThat(forJson(TYPES)).extractingJsonPathValue("@.str").isEqualTo("foo");
# \r\n\t}']
