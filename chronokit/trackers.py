import functools, inspect, time, warnings
from typing import Any, Callable, Optional


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
            'stop': []
        }
        
    def _double_call_blocker(
        function: Callable[['TimeTracker'], Any]
    ) -> Callable[['TimeTracker'], Any]:
        
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
                    warnings.warn_explicit(
                        message=f'Double call blocked: {function.__qualname__}',
                        category=UserWarning,
                        filename=frame_info[0],
                        lineno=frame_info[1]
                    )
                else:
                    self.is_running = True
                    return function(self, *args, **kwargs)

            elif function.__name__ == 'stop':
                if not self.is_running:
                    warnings.warn_explicit(
                        message=f'Double call blocked: {function.__qualname__}',
                        category=UserWarning,
                        filename=frame_info[0],
                        lineno=frame_info[1]
                    )
                else:
                    self.is_running = False
                    return function(self, *args, **kwargs)
                
        return wrapper

    @_double_call_blocker
    def start(
        self: 'TimeTracker'
    ) -> float:
        
        start_time = time.perf_counter()
        self.track_log['start'].append(start_time)
        
        return start_time
    
    @_double_call_blocker
    def stop(
        self: 'TimeTracker'
    ) -> float:
        
        stop_time = time.perf_counter()
        self.track_log['stop'].append(stop_time)
        
        self.total_elapsed_time = (
            self.track_log['stop'][-1] - 
            self.track_log['start'][0]
        ) 
        if self.elapsed_time is None:
            self.elapsed_time = (
                self.track_log['stop'][-1] - 
                self.track_log['start'][-1]
            )
        else:
            self.elapsed_time += (
                self.track_log['stop'][-1] - 
                self.track_log['start'][-1]
            )

        return stop_time           


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
