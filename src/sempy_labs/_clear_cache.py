import sempy.fabric as fabric
from sempy_labs._helper_functions import resolve_dataset_id, is_default_semantic_model
from typing import Optional
import sempy_labs._icons as icons


def clear_cache(dataset: str, workspace: Optional[str] = None):
    """
    Clears the cache of a semantic model.
    See `here <https://learn.microsoft.com/analysis-services/instances/clear-the-analysis-services-caches?view=asallproducts-allversions>`_ for documentation.

    Parameters
    ----------
    dataset : str
        Name of the semantic model.
    workspace : str, default=None
        The Fabric workspace name.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    """

    workspace = fabric.resolve_workspace_name(workspace)
    if is_default_semantic_model(dataset=dataset, workspace=workspace):
        raise ValueError(
            f"{icons.red_dot} Cannot run XMLA operations against a default semantic model. Please choose a different semantic model. "
            "See here for more information: https://learn.microsoft.com/fabric/data-warehouse/semantic-models"
        )

    dataset_id = resolve_dataset_id(dataset=dataset, workspace=workspace)

    xmla = f"""
            <ClearCache xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
                <Object>
                    <DatabaseID>{dataset_id}</DatabaseID>
                </Object>
            </ClearCache>
            """
    fabric.execute_xmla(dataset=dataset, xmla_command=xmla, workspace=workspace)
    print(
        f"{icons.green_dot} Cache cleared for the '{dataset}' semantic model within the '{workspace}' workspace."
    )


def backup_semantic_model(
    dataset: str,
    file_path: str,
    allow_overwrite: Optional[bool] = True,
    apply_compression: Optional[bool] = True,
    workspace: Optional[str] = None,
):
    """
    `Backs up <https://learn.microsoft.com/azure/analysis-services/analysis-services-backup>`_ a semantic model to the ADLS Gen2 storage account connected to the workspace.

    Parameters
    ----------
    dataset : str
        Name of the semantic model.
    file_path : str
        The ADLS Gen2 storage account location in which to backup the semantic model. Always saves within the 'power-bi-backup/<workspace name>' folder.
        Must end in '.abf'.
        Example 1: file_path = 'MyModel.abf'
        Example 2: file_path = 'MyFolder/MyModel.abf'
    allow_overwrite : bool, default=True
        If True, overwrites backup files of the same name. If False, the file you are saving cannot have the same name as a file that already exists in the same location.
    apply_compression : bool, default=True
        If True, compresses the backup file. Compressed backup files save disk space, but require slightly higher CPU utilization.
    workspace : str, default=None
        The Fabric workspace name.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    """

    if not file_path.endswith(".abf"):
        raise ValueError(
            f"{icons.red_dot} The backup file for restoring must be in the .abf format."
        )

    workspace = fabric.resolve_workspace_name(workspace)

    tmsl = {
        "backup": {
            "database": dataset,
            "file": file_path,
            "allowOverwrite": allow_overwrite,
            "applyCompression": apply_compression,
        }
    }

    fabric.execute_tmsl(script=tmsl, workspace=workspace)
    print(
        f"{icons.green_dot} The '{dataset}' semantic model within the '{workspace}' workspace has been backed up to the '{file_path}' location."
    )


def restore_semantic_model(
    dataset: str,
    file_path: str,
    allow_overwrite: Optional[bool] = True,
    ignore_incompatibilities: Optional[bool] = True,
    force_restore: Optional[bool] = False,
    workspace: Optional[str] = None,
):
    """
    `Restores <https://learn.microsoft.com/power-bi/enterprise/service-premium-backup-restore-dataset>`_ a semantic model based on a backup (.abf) file
    within the ADLS Gen2 storage account connected to the workspace.

    Parameters
    ----------
    dataset : str
        Name of the semantic model.
    file_path : str
        The location in which to backup the semantic model. Must end in '.abf'.
        Example 1: file_path = 'MyModel.abf'
        Example 2: file_path = 'MyFolder/MyModel.abf'
    allow_overwrite : bool, default=True
        If True, overwrites backup files of the same name. If False, the file you are saving cannot have the same name as a file that already exists in the same location.
    ignore_incompatibilities : bool, default=True
        If True, ignores incompatibilities between Azure Analysis Services and Power BI Premium.
    force_restore: bool, default=False
        If True, restores the semantic model with the existing semantic model unloaded and offline.
    workspace : str, default=None
        The Fabric workspace name.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    """
    # https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-backup-restore-dataset

    if not file_path.endswith(".abf"):
        raise ValueError(
            f"{icons.red_dot} The backup file for restoring must be in the .abf format."
        )

    workspace = fabric.resolve_workspace_name(workspace)

    tmsl = {
        "restore": {
            "database": dataset,
            "file": file_path,
            "allowOverwrite": allow_overwrite,
            "security": "copyAll",
            "ignoreIncompatibilities": ignore_incompatibilities,
        }
    }

    if force_restore:
        tmsl["restore"]["forceRestore"] = force_restore

    fabric.execute_tmsl(script=tmsl, workspace=workspace)

    print(
        f"{icons.green_dot} The '{dataset}' semantic model has been restored to the '{workspace}' workspace based on teh '{file_path}' backup file."
    )
