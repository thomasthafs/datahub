import { Button, Icon, colors } from '@components';
import { ActionsBar } from '@components/components/ActionsBar/ActionsBar';
import { PencilSimple } from '@phosphor-icons/react/dist/csr/PencilSimple';
import React, { useCallback } from 'react';
import styled from 'styled-components';

import { useUserContext } from '@app/context/useUserContext';
import analytics, { EventType } from '@app/analytics';
import { usePageTemplateContext } from '@app/homeV3/context/PageTemplateContext';

const EditButton = styled(Button)`
    align-self: flex-end;
    margin-bottom: 8px;
`;

const DoneBar = styled(ActionsBar)`
    margin-bottom: 8px;
`;

const Label = styled.span`
    font-weight: 600;
    font-size: 14px;
    color: ${colors.gray[600]};
`;

export default function HomePageSettingsButtonWrapper() {
    const { isEditingPersonalTemplate, setIsEditingPersonalTemplate, setIsEditingGlobalTemplate, resetTemplateToDefault } =
        usePageTemplateContext();
    const userContext = useUserContext();
    const canManageGlobalTemplate = userContext.platformPrivileges?.manageHomePageTemplates || false;

    const onClickEdit = useCallback(() => {
        setIsEditingPersonalTemplate(true);
        analytics.event({ type: EventType.HomePageTemplatePersonalTemplateEditingStart });
    }, [setIsEditingPersonalTemplate]);

    const onClickEditOrg = useCallback(() => {
        setIsEditingGlobalTemplate(true);
        analytics.event({ type: EventType.HomePageTemplateGlobalTemplateEditingStart });
    }, [setIsEditingGlobalTemplate]);

    const onClickDone = useCallback(() => {
        setIsEditingPersonalTemplate(false);
        analytics.event({ type: EventType.HomePageTemplatePersonalTemplateEditingDone });
    }, [setIsEditingPersonalTemplate]);

    const onClickReset = useCallback(() => {
        resetTemplateToDefault();
        setIsEditingPersonalTemplate(false);
    }, [resetTemplateToDefault, setIsEditingPersonalTemplate]);

    if (isEditingPersonalTemplate) {
        return (
            <DoneBar dataTestId="editing-personal-template-bar">
                <Label>Editing your home page</Label>
                <Button variant="outline" onClick={onClickReset} data-testid="reset-to-default-button">
                    Reset to default
                </Button>
                <Button onClick={onClickDone} data-testid="finish-editing-personal-template">
                    Done
                </Button>
            </DoneBar>
        );
    }

    return (
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginBottom: 8 }}>
            <EditButton
                variant="outline"
                size="sm"
                onClick={onClickEdit}
                data-testid="edit-home-page-button"
            >
                <Icon icon={PencilSimple} />
                Customize home page
            </EditButton>
            {canManageGlobalTemplate && (
                <EditButton
                    variant="outline"
                    size="sm"
                    onClick={onClickEditOrg}
                    data-testid="edit-org-default-button"
                >
                    <Icon icon={PencilSimple} />
                    Edit org default
                </EditButton>
            )}
        </div>
    );
}
