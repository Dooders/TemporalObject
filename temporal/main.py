import uuid
from collections import deque
from typing import Any

from temporal.util import LimitedDict


class TemporalObject:
    """
    A custom python object for storing and managing states in a temporal sequence.

    This class utilizes a deque with a fixed temporal length (maxlen) to maintain
    a rolling buffer of states.

    Each state can be indexed by an integer, a string ID, or a slice. The class
    also tracks the current state index within the buffer.

    Parameters
    ----------
    temporal_depth : int
        The maximum number of states to store.

    Methods
    -------
    update(object_state: dict, temporal_id: str = None) -> str:
        Adds the object's state to the buffer.
    get(key: str, relative_index: int = 0) -> dict:
        Returns the value of the object with the given key and relative index.
    current() -> dict:
        Returns the most recent state.
    """

    def __init__(self, temporal_depth: int = None) -> None:
        """
        Parameters
        ----------
        temporal_depth : int, optional
            The maximum number of states to store. If None, the buffer is unlimited.
        """
        self._buffer = deque(maxlen=temporal_depth)
        self._id_index = LimitedDict(temporal_depth)

    def _add(self, id: str, state: dict) -> None:
        """
        Appends a state to the buffer.

        Parameters
        ----------
        id : str
            The ID of the state.
        state : dict
            The state to add to the buffer.
        """
        self._id_index[id] = state
        self._buffer.append(state)

    def update(self, object_state: dict, temporal_id: str = None) -> str:
        """
        Adds the object's state to the buffer.

        Parameters
        ----------
        object_state : dict
            The object's state to add to the buffer.
        temporal_id : str, optional
            The temporal ID of the object. If not provided, the object's temporal
            ID is used.
        """
        if temporal_id is None:
            temporal_id = str(uuid.uuid4())
        self._add(temporal_id, object_state)

        return temporal_id

    def get(self, key: str, relative_index: int = 0, default: Any = None) -> dict:
        """
        Returns the value of the object with the given key and relative index.

        Parameters
        ----------
        key : str
            The key of the object.
        relative_index : int, optional
            The relative index of the object.
        default:
            Optional. A value to return if the specified key does not exist.
            Default value None
        """
        return self[relative_index][key] if key in self[relative_index] else default

    def _get_by_temporal_id(self, temporal_id: str) -> dict:
        """
        Returns the state of the object with the given temporal ID.

        Parameters
        ----------
        temporal_id : str
            The temporal ID of the object.
        """
        return self._id_index.get(temporal_id, None)

    def __len__(self) -> int:
        """
        Returns the number of states in the buffer.

        Returns
        -------
        int
            The number of states in the buffer.
        """
        return len(self._buffer)

    def __contains__(self, key: str) -> bool:
        """
        Returns whether the temporal ID is in the buffer.
        """
        return key in self._id_index

    def __setitem__(self, key: str, value: dict) -> None:
        """
        Sets the value of the key.
        """
        self._id_index[key] = value

    def __delitem__(self, key: str) -> None:
        """
        Deletes the value of the key.
        """
        del self._id_index[key]

    def __iter__(self) -> dict:
        """
        Returns an iterator over the states in the buffer.
        """
        return iter(self._buffer)

    def __getitem__(self, index: int | slice | str) -> dict:
        """
        Returns the state at the given index.

        If index is a string, it is assumed to be a temporal ID.

        If index is a slice, it is assumed to be a range of relative indices.

        If index is an integer, it is assumed to be a relative index.

        Parameters
        ----------
        index : int | slice | str
            The index of the state to return. Can be by position (int),
            by temporal ID (str), or by slice.

        Returns
        -------
        dict
            The state at the given index.
        """
        # If index is an integer, return the state at the given index
        if isinstance(index, int):
            # If index is negative
            if index < 0:
                index = abs(index)
            # Check if the index is within the valid range
            if index < 0 or index >= len(self._buffer):
                raise IndexError("Index out of range")
            # Return the state at the given index
            return self._buffer[-1 - index]

        # If index is a slice, return the states in the given range
        elif isinstance(index, slice):
            # Convert the slice to a list of indices
            start, stop, step = index.indices(len(self._buffer))
            # Return the states at the given indices
            return [self._buffer[i] for i in range(start, stop, step)]

        elif isinstance(index, str):
            return self._get_by_temporal_id(index)
        else:
            raise TypeError("Invalid argument type")

    def recent(self, n: int = 1) -> dict:
        """
        Returns the most recent n states.
        """
        return self[-n:]

    @property
    def current(self) -> dict:
        """
        Returns the current state.

        Returns
        -------
        dict
            The current state.
        """
        return self._buffer[-1]
