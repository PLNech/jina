from typing import Dict, List, Tuple, Union

from jina.helper import colored


from .base import BaseStore
from ..models import DaemonID
from ..models.enums import WorkspaceState
from ..dockerize import Dockerizer

from ..models.workspaces import WorkspaceArguments, WorkspaceItem, WorkspaceMetadata, WorkspaceStoreStatus

from .. import __rootdir__, __dockerfiles__, jinad_args


class WorkspaceStore(BaseStore):

    _kind = 'workspace'
    _status_model = WorkspaceStoreStatus

    @BaseStore.dump
    def add(self,
            id: DaemonID,
            value: WorkspaceState, **kwargs):
        if isinstance(value, WorkspaceState):
            self[id] = WorkspaceItem(state=value)
        return id

    @BaseStore.dump
    def update(self,
               id: DaemonID,
               value: Union[WorkspaceItem, WorkspaceState, WorkspaceArguments, WorkspaceMetadata],
               **kwargs) -> DaemonID:
        if id not in self:
            raise KeyError(f'workspace {id} not found in store')

        if isinstance(value, WorkspaceItem):
            self[id] = value
        elif isinstance(value, WorkspaceArguments):
            self[id].arguments = value
        elif isinstance(value, WorkspaceMetadata):
            self[id].metadata = value
        elif isinstance(value, WorkspaceState):
            self[id].state = value
        else:
            self._logger.error(f'invalid arguments for workspace: {value}')
        return id

    @BaseStore.dump
    def delete(self, id: DaemonID, **kwargs):
        if id not in self:
            raise KeyError(f'{colored(str(id), "cyan")} not found in store.')
        Dockerizer.rm_image(id=self[id].metadata.image_id)
        Dockerizer.rm_network(id=self[id].metadata.network)
        del self[id]
        self._logger.success(
            f'{colored(str(id), "cyan")} is released from the store.'
        )
