export default function useIsTemplateEditable(isEditingPersonal: boolean, isEditingGlobal: boolean) {
    return isEditingPersonal || isEditingGlobal;
}
