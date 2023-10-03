from pathlib import Path
import functools, inspect, time, warnings
from typing import Any, Callable, Optional, Union


class TimeTracker:


    def __init__(
        self: 'TimeTracker',
        name: Optional[str] = None
    ) -> None:
        
        self.name = name
        self.is_running = False
        self.elapsed_time = None
        self.total_elapsed_time = None
        self.track_log = {
            'start': [],
            'stop': [],
            'blocked': []
        }

    def _bug_blocker(
        function: Callable[['TimeTracker'], Any]
    ) -> Callable[['TimeTracker'], Any]:
        
        def _save_block_log(
            self: 'TimeTracker',
            line: int,
            local: Union[Path, str],
            reason: str
        ) -> None:
            warnings.warn_explicit(
                message=f'Blocked: {function.__qualname__}; {reason}',
                category=UserWarning,
                filename=local,
                lineno=line
            )
            self.track_log['blocked'].append(
                (
                    local, 
                    line,
                    f'Blocked: {function.__qualname__}; {reason}'
                )
            )

        @functools.wraps(function)
        def wrapper(
            self: 'TimeTracker',
            *args,
            **kwargs
        ) -> Any:
               
            frame_info = inspect.getframeinfo(
                inspect.currentframe().f_back
            )
            if function.__name__ == 'start':
                if self.is_running:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason='Double call!'    
                    )
                else:
                    self.is_running = True
                    return function(self, *args, **kwargs)

            elif function.__name__ == 'stop':
                if not self.is_running:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason='Double call!'    
                    )
                else:
                    self.is_running = False
                    return function(self, *args, **kwargs)
            
            elif function.__name__ == 'get_elapsed_time':
                if not self.track_log['start']:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason="The tracker hasn't started yet!"    
                    )
                    return None
                elif not self.track_log['stop']:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason="The tracker hasn't been completed yet!"
                    )
                    return None
                elif self.is_running:
                    warnings.warn(
                        message='Opened tracker. Only closed trackers will be calculated.',
                        category=UserWarning
                    )
                    return function(self, *args, **kwargs)
        return wrapper

    @_bug_blocker
    def start(
        self: 'TimeTracker'
    ) -> float:
        
        start_time = time.perf_counter()
        self.track_log['start'].append(start_time)
        
        return start_time
    
    @_bug_blocker
    def stop(
        self: 'TimeTracker'
    ) -> float:
        
        stop_time = time.perf_counter()
        self.track_log['stop'].append(stop_time)

        return stop_time           

    @_bug_blocker
    def get_elapsed_time(
        self: 'TimeTracker'
    ) -> Union[float, None]:
        
        self.total_elapsed_time = (
            self.track_log['stop'][-1] - 
            self.track_log['start'][0]
        ) 
        if self.elapsed_time is None:
                self.elapsed_time = (
                    self.track_log['stop'][-1] - 
                    self.track_log['start'][-1]
                )
        start_log = self.track_log['start']
        stop_log = self.track_log['stop']

        if self.is_running:
            start_log.pop()

        for start, stop in zip(start_log, stop_log):        
            self.elapsed_time += stop - start
    
        return self.elapsed_time
    

class TimeTrackers:

    
    def __init__(
        self: 'TimeTrackers'
    ) -> None:
        
        self.timers = {}
        self.start_time = None
        self.end_time = None
        

    def add(
        self: 'TimeTrackers',
        name: Optional[str] = None
    ) -> None:
        pass


class ExecutionTimeTracker:


    def __init__(
        self: 'ExecutionTimeTracker',
        function: Callable[[Any], Any]
    ) -> None:
        
        """
        A class to time the execution of a provided function!
        To use this class, decorate your function with it!

        Args:
            - function (callable): The function to be timed.
            
        Attributes:
            - function (callable): The function to be timed.
            - exec_start_time (float or None): Start time of the function execution.
            - exec_end_time (float or None): End time of the function execution.
            - exec_elapsed_time (float or None): Elapsed time taken by the function.
        """
        
        self.function = function
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

    def __call__(
        self: 'ExecutionTimeTracker', 
        *args: Any, 
        **kwargs: Any
    ) -> Any:
        
        self.start_time = time.perf_counter()
        self.func_out = self.function(
            *args, **kwargs
        )
        self.end_time = time.perf_counter()
        self.elapsed_time = self.end_time - self.start_time

        return self.func_out



a = TimeTracker

a.start()